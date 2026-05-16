"""
行业/个股跟踪报告生成脚本。

输入:
- query (用户原始问题)

输出(JSON):
- title: 报告标题
- content: 按 skill 规范生成的正文(仅总结章节)
- attachments: PDF/DOCX 保存路径

错误处理:
- ERROR_ENTITY -> "目前暂不支持此类实体体进行分析。"
- 其他异常 -> "报告生成服务暂时不可用，请稍后重试。"
"""

import argparse
import base64
import json
import os
import socket
import sys
import urllib.error
import urllib.request
import traceback
import uuid
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
API_URL = "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/write/tracking/report"
TOOL_NAME = "行业/个股跟踪报告"
SKILL_SLUG = "industry_stock_tracker"
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / SKILL_SLUG

ERROR_ENTITY_MSG = "目前暂不支持此类实体体进行分析。"
GENERAL_ERROR_MSG = "报告生成服务暂时不可用，请稍后重试。"


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


def _clean_report_text(text: str) -> str:
    if not text:
        return ""
    cleaned = text
    # 去掉内部协议链接（如 blockTitle://、table://）
    cleaned = re.sub(r"\[[^\]]*\]\((?:blockTitle|table)://[^)]*\)", "", cleaned)
    # 普通 markdown 链接转纯文本，仅保留标题
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    # 规范化换行和空白
    cleaned = cleaned.replace("\\n", "\n")
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _read_query_from_stdin() -> str:
    raw = sys.stdin.read().strip()
    if not raw:
        return ""
    try:
        payload = json.loads(raw)
        if isinstance(payload, dict):
            return _safe_str(payload.get("query", ""))
        if isinstance(payload, str):
            return payload.strip()
    except json.JSONDecodeError:
        return raw
    return ""

def _call_api(query: str, timeout: float = 1200.0) -> Dict[str, Any]:
    req_body = json.dumps({"query": query}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        method="POST",
        data=req_body,
        headers={
            "Content-Type": "application/json",
            "em_api_key": EM_API_KEY,
            "Accept": "application/json",
            "User-Agent": "industry-stock-tracker/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = getattr(resp, "status", None) or resp.getcode()
            content = resp.read()

    except urllib.error.HTTPError as e:
        raw = e.read() if hasattr(e, "read") else b""
        snippet = raw[:500].decode("utf-8", errors="replace")
        raise ApiCallError("HTTP_ERROR", "status={0}, body={1}".format(e.code, snippet))
    except socket.timeout:
        raise ApiCallError("TIMEOUT", "read operation timed out")
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, socket.timeout):
            raise ApiCallError("TIMEOUT", "read operation timed out")
        raise ApiCallError("NETWORK_ERROR", _safe_str(reason))

    text = content.decode("utf-8", errors="replace")
    if status_code and int(status_code) >= 400:
        raise ApiCallError("HTTP_ERROR", "status={0}, body={1}".format(status_code, text[:500]))

    try:
        parsed = json.loads(text) if text else {}
    except Exception:
        raise ApiCallError("INVALID_JSON", text[:500])

    return parsed if isinstance(parsed, dict) else {"data": parsed}


def _unwrap_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    for key in ("data", "result", "content"):
        node = payload.get(key)
        if isinstance(node, dict):
            return node
    return payload

def _default_output_dir() -> str:
    """
    Allow overriding attachment output directory via env:
      INDUSTRY_STOCK_TRACKER_OUTPUT_DIR
    """
    env = os.environ.get("INDUSTRY_STOCK_TRACKER_OUTPUT_DIR", "").strip()
    return env or str(DEFAULT_OUTPUT_DIR)

def _decode_attachment_base64(data: Dict[str, Any], output_dir: str) -> List[Dict[str, str]]:
    attachments: List[Dict[str, str]] = []
    os.makedirs(output_dir, exist_ok=True)

    file_map = [
        ("wordBase64", "docx", "DOCX"),
        ("pdfBase64", "pdf", "PDF"),
    ]
    article_id = _safe_str(data.get("articleId"), default=uuid.uuid4().hex)
    safe_article_id = re.sub(r"[^a-zA-Z0-9_-]+", "_", article_id)

    for key, ext, ftype in file_map:
        b64_str = _safe_str(data.get(key))
        if not b64_str:
            continue
        try:
            raw = base64.b64decode(b64_str)
        except Exception:
            continue
        file_name = "{0}_{1}.{2}".format(safe_article_id, ftype.lower(), ext)
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(raw)
        attachments.append({"type": ftype, "url": file_path})
    return attachments

def _render_content(entity_type: str, summary_content: str) -> str:
    return (
        f"已生成{entity_type}跟踪报告，包括行业和个股的多种信源摘要。"
        "此处省略正文内容，仅展示总结章节，如需查看完整内容，请查看附件获取报告详情。\n\n"
        f"{summary_content}"
    )


def build_report_output(
    query: str,
    payload: Dict[str, Any]
) -> Dict[str, Any]:
    raw_data = payload.get("data") if isinstance(payload, dict) else None
    data = _unwrap_data(payload)
    code = _safe_str(payload.get("code") if isinstance(payload, dict) else "")
    message = _safe_str(payload.get("message") if isinstance(payload, dict) else "")

    # 明确错误码处理
    if code == "ERROR_ENTITY" or _safe_str(data.get("code")) == "ERROR_ENTITY":
        return {"ok": False, "error_code": "ERROR_ENTITY", "message": ERROR_ENTITY_MSG}

    # 简化规则：message 有值且 data 为空，直接返回接口 message
    if message and not raw_data:
        return {
            "ok": False,
            "error_code": code or "API_ERROR",
            "message": message,
        }

    title = _safe_str(data.get("title"), default="行业/个股跟踪报告")
    share_url = _safe_str(data.get("shareUrl"), default="无")
    entity_type = _safe_str(data.get("entityType") or data.get("entity_type"), default="行业/个股")
    summary = _safe_str(data.get("content"), default="")
    attachments = _decode_attachment_base64(data, _default_output_dir())
    # traceability = _extract_traceability(data)

    if not summary:
        summary = "暂无总结内容，请查看附件获取报告详情。"

    output = {
        "ok": True,
        "tool": TOOL_NAME,
        "query": query,
        "title": title,
        "content": _render_content(entity_type=entity_type, summary_content=summary),
        "attachments": attachments,
        "share_url": share_url
    }
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成行业/个股跟踪报告")
    parser.add_argument("--query", type=str, default="", help="用户查询文本")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    query = _safe_str(args.query) or _read_query_from_stdin()
    if not query:
        print(
            json.dumps(
                {"ok": False, "error_code": "BAD_REQUEST", "message": "缺少 query 参数"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    try:
        payload = _call_api(query=query)
        output = build_report_output(
            query=query,
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


if __name__ == "__main__":
    main()
