"""
OpenClaw mx_finance_search skill runtime.

This module is intentionally self-contained:
- No hard-coded user identity.
- Runtime defaults are defined in-code (no environment reads).
"""

import argparse
import asyncio
import json
import os
import uuid
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request
from typing import Dict, Any, Optional


EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "mx_finance_search"

print('默认输出目录为：',DEFAULT_OUTPUT_DIR.absolute())
TIMEOUT_SECONDS = 15
# MCP 服务器地址
MCP_URL = "https://ai-saas.eastmoney.com/proxy/b/mcp/tool/searchNews"

def get_metadata(
        query: str = "",
        selectType: str = "",
) -> dict:
    """
    生成 MCP 调用所需的 metadata 字典。
    自动补充 callId，并将 EM_API_KEY 注入 userInfo。
    返回值可直接作为请求体中的上下文字段使用。
    """
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    return {
        "query": query,
        "selectType": selectType,
        "toolContext": {
            "callId": call_id,
            "userInfo": {
                "userId": user_id,
            },
        },
    }

def _extract_content(raw: Dict[str, Any]) -> str:
    """
    从新闻接口返回数据中提取可读文本内容。
    优先读取常见文本字段，兼容 data/result 包裹结构。
    当文本字段缺失时，回退为格式化后的 JSON 字符串。
    """
    if not isinstance(raw, dict):
        return ""

    # Common envelope format: {"data": {...}} / {"result": {...}}
    for wrapper_key in ("data", "result"):
        wrapped = raw.get(wrapper_key)
        if isinstance(wrapped, dict):
            nested = _extract_content(wrapped)
            if nested:
                return nested

    for key in ("llmSearchResponse", "searchResponse", "content", "answer", "summary"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False, indent=2)

    return json.dumps(raw, ensure_ascii=False, indent=2)


def _load_optional_tool_context() -> Dict[str, Any]:
    """
    构造请求所需的 toolContext 默认值。
    目前仅生成可追踪的 callId 字段。
    返回结果用于下游接口请求的上下文字段。
    """
    return {"callId": f"call_{uuid.uuid4().hex[:12]}"}


def _extract_error_message(body: str) -> str:
    """
    从错误响应体中提取可展示的错误信息。
    优先读取 msg/message/error 字段，失败时截断原文。
    用于统一构造上层异常提示内容。
    """
    body = (body or "").strip()
    if not body:
        return ""
    try:
        data = json.loads(body)
    except Exception:
        return body[:200]
    if isinstance(data, dict):
        for key in ("msg", "message", "error"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return body[:200]


def _http_call_search_news(query: str) -> Dict[str, Any]:
    """
    调用 searchNews 接口并返回解析后的 JSON 数据。
    负责构建请求头、超时控制和 HTTP 异常处理。
    若响应不是字典结构，会自动包装为 {"data": ...}。
    """
    api_key = EM_API_KEY.strip()
    if not api_key:
        raise ValueError("EM_API_KEY is required.")

    timeout_raw = str(TIMEOUT_SECONDS).strip()
    try:
        timeout_seconds = max(1, int(timeout_raw))
    except ValueError as exc:
        raise ValueError("FINANCIAL_SEARCH_HTTP_TIMEOUT must be an integer >= 1.") from exc

    payload = {
        "query": query,
        "toolContext": _load_optional_tool_context(),
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        url=MCP_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "em_api_key": api_key,
        },
    )

    try:
        with urllib_request.urlopen(req, timeout=timeout_seconds) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
    except urllib_error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        message = _extract_error_message(err_body) or f"http status {exc.code}"
        raise RuntimeError(f"News API request failed: {message}") from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"News API request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("News API returned invalid JSON response.") from exc
    return parsed if isinstance(parsed, dict) else {"data": parsed}


async def query_financial_news(
    query: str,
    output_dir: Optional[Path] = None,
    save_to_file: bool = True,
) -> Dict[str, Any]:
    """
    按自然语言查询金融资讯并整理统一结果结构。
    内部异步执行 HTTP 请求，提取文本内容并按需落盘。
    返回 query/content/raw/output_path，异常时附带 error。
    """
    query = (query or "").strip()
    if not query:
        return {
            "query": "",
            "content": "",
            "output_path": None,
            "raw": None,
            "error": "query is empty",
        }

    out_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {"query": query, "content": "", "output_path": None, "raw": None}
    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _http_call_search_news, query)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["raw"] = raw
    content = _extract_content(raw)
    result["content"] = content

    if save_to_file and content:
        unique_suffix = uuid.uuid4().hex[:8]
        output_path = out_dir / f"mx_finance_search_{unique_suffix}.txt"
        output_path.write_text(content, encoding="utf-8")
        result["output_path"] = str(output_path)

    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    """
    构建命令行参数解析器。
    支持位置参数 query 与 --no-save 开关。
    返回配置完成的 ArgumentParser 实例。
    """
    parser = argparse.ArgumentParser(
        description="Query financial news/reports by natural language and optionally save output."
    )
    parser.add_argument("query", nargs="*", help="Natural language query text.")
    parser.add_argument("--no-save", action="store_true", help="Do not write result to local file.")
    return parser


def run_cli() -> None:
    """
    CLI 入口函数。
    解析命令行或标准输入中的查询文本并执行异步检索。
    根据执行结果输出内容、保存路径或错误信息。
    """
    parser = _build_arg_parser()
    args = parser.parse_args()

    query = " ".join(args.query).strip()
    if not query:
        import sys

        query = (sys.stdin.read() or "").strip()

    if not query:
        parser.print_help()
        raise SystemExit(1)

    async def _main() -> None:
        result = await query_financial_news(query=query, save_to_file=not args.no_save)
        if "error" in result:
            print(f"Error: {result['error']}")
            raise SystemExit(2)
        if result.get("output_path"):
            print(f"Saved: {result['output_path']}")
        print(result.get("content", ""))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()
