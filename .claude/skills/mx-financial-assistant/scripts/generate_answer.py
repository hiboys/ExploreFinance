"""
金融问答脚本。

基于东方财富金融数据库，通过自然语言问题调用金融问答接口，
返回回答结果（标准模式/深度思考模式），包括总结回答内容
（含选股类数据结果）及溯源参考（资讯、公告、数据等）。
"""

import argparse
import asyncio
import json
import os
import sys
import traceback
from typing import Any, Dict, List

import httpx

EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
API_URL = "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/ask"
TOOL_NAME = "金融问答"

GENERAL_ERROR_MSG = "金融问答服务暂时不可用，请稍后重试。"


class ApiCallError(Exception):
    def __init__(self, code: str, detail: str):
        Exception.__init__(self, detail)
        self.code = code
        self.detail = detail


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _read_question_from_stdin() -> str:
    raw = sys.stdin.read().strip()
    if not raw:
        return ""
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            return _safe_str(payload.get("query") or payload.get("question") or "")
        if isinstance(payload, str):
            return payload.strip()
    except json.JSONDecodeError:
        return raw
    return ""


async def _call_api(question: str, deep_think: bool = False, timeout: float = 600.0) -> Dict[str, Any]:
    body: Dict[str, Any] = {"question": question}
    if deep_think:
        body["deepThink"] = True

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                API_URL,
                json=body,
                headers={
                    "Content-Type": "application/json",
                    "em_api_key": EM_API_KEY,
                    "Accept": "application/json",
                    "User-Agent": "mx-financial-assistant/1.0",
                },
            )
    except httpx.TimeoutException:
        raise ApiCallError("TIMEOUT", "read operation timed out")
    except httpx.RequestError as e:
        raise ApiCallError("NETWORK_ERROR", _safe_str(e))

    text = resp.text
    if resp.status_code >= 400:
        raise ApiCallError("HTTP_ERROR", "status={0}, body={1}".format(resp.status_code, text[:500]))

    try:
        parsed = resp.json() if text else {}
    except Exception:
        raise ApiCallError("INVALID_JSON", text[:500])

    return parsed if isinstance(parsed, dict) else {"data": parsed}


def _extract_display_data(payload: Dict[str, Any]) -> str:
    """从 data.displayData 中提取模型回答（Markdown 格式）。"""
    data = payload.get("data")
    if isinstance(data, dict):
        return _safe_str(data.get("displayData"))
    return ""


def _extract_references(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    从 data.refIndexList 中提取溯源参考。

    每个元素包含:
      - refId (Number): 引用编号
      - type (String): 数据类型 (查数 | 公告 | 研报 | 资讯 | 选股/基)
      - referenceType (String): CITED_REFERENCE(直接引用) | OTHER_REFERENCE(扩展引用)
      - markdown (String, 可选): type=查数/选股/基 时存在，结构化数据表格
      - title (String, 可选): type=资讯 时存在，资讯标题
      - jumpUrl (String, 可选): type=资讯 时可能存在，原始文档链接
      - source (String, 可选): 资讯/舆情等来源站点名；可能在顶层或 data.source
    """
    refs: List[Dict[str, Any]] = []
    data = payload.get("data")
    if not isinstance(data, dict):
        return refs

    ref_list = data.get("refIndexList")
    if not isinstance(ref_list, list):
        return refs

    for item in ref_list:
        if not isinstance(item, dict):
            continue
        ref_entry: Dict[str, Any] = {
            "refId": item.get("refId"),
            "type": _safe_str(item.get("type")),
            "referenceType": _safe_str(item.get("referenceType")),
        }
        markdown_val = item.get("markdown")
        if markdown_val is not None:
            ref_entry["markdown"] = _safe_str(markdown_val)

        title_val = item.get("title")
        if title_val is not None:
            ref_entry["title"] = _safe_str(title_val)

        jump_url_val = item.get("jumpUrl")
        if jump_url_val is not None:
            ref_entry["jumpUrl"] = _safe_str(jump_url_val)

        source_val = item.get("source")
        if source_val is None:
            nested = item.get("data")
            if isinstance(nested, dict):
                source_val = nested.get("source")
        if source_val is not None:
            ref_entry["source"] = _safe_str(source_val)

        refs.append(ref_entry)

    return refs


def build_qa_output(
    question: str,
    deep_think: bool,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    code = payload.get("code")
    message = _safe_str(payload.get("message"))
    stack = payload.get("stack")

    if isinstance(code, int) and code != 200:
        return {
            "ok": False,
            "error_code": "API_ERROR",
            "message": message or GENERAL_ERROR_MSG,
            "stack": _safe_str(stack) if stack else None,
        }

    answer = _extract_display_data(payload)
    references = _extract_references(payload)

    if not answer:
        return {
            "ok": False,
            "error_code": "EMPTY_RESPONSE",
            "message": message or "未获取到有效回答，请稍后重试。",
        }

    output: Dict[str, Any] = {
        "ok": True,
        "tool": TOOL_NAME,
        "question": question,
        "deep_think": deep_think,
        "answer": answer,
        "references": references,
    }
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="金融问答")
    parser.add_argument("--query", type=str, default="", help="用户问题文本")
    parser.add_argument(
        "--deep-think",
        action="store_true",
        default=False,
        help="是否开启深度思考模式",
    )
    return parser.parse_args()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = parse_args()
    question = _safe_str(args.query) or _read_question_from_stdin()
    deep_think = args.deep_think

    if not _safe_str(EM_API_KEY):
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "MISSING_CREDENTIAL",
                    "message": "请先设置 EM_API_KEY 环境变量。",
                },
                ensure_ascii=False,
            )
        )
        sys.exit(2)

    if not question:
        print(
            json.dumps(
                {"ok": False, "error_code": "BAD_REQUEST", "message": "请输入您想问的问题。"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    async def _main() -> None:
        try:
            payload = await _call_api(question=question, deep_think=deep_think)
            output = build_qa_output(
                question=question,
                deep_think=deep_think,
                payload=payload,
            )
            print(json.dumps(output, ensure_ascii=False))
            sys.exit(0 if output.get("ok") else 2)
        except ApiCallError as e:
            err = {
                "ok": False,
                "error_code": e.code,
                "message": GENERAL_ERROR_MSG,
                "detail": e.detail,
            }
            print(json.dumps(err, ensure_ascii=False))
            sys.exit(2)
        except Exception as e:
            err = {
                "ok": False,
                "error_code": "UNEXPECTED_ERROR",
                "message": GENERAL_ERROR_MSG,
                "detail": _safe_str(e),
                "traceback": traceback.format_exc(limit=8),
            }
            print(json.dumps(err, ensure_ascii=False))
            sys.exit(2)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
