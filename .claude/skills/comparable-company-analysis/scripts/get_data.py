"""
OpenClaw comparable_company_analysis data fetcher.

This module only fetches and normalizes API response.
It does NOT persist raw API payload to local files.
"""

import argparse
import asyncio
import json
import os
from typing import Any, Dict, List
from urllib import error as urllib_error
from urllib import request as urllib_request

EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
COMPARE_API_URL = "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/comparable-company-analysis"
TIMEOUT_SECONDS = 60


def _extract_error_message(body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    try:
        data = json.loads(body)
    except Exception:
        return body[:300]
    if isinstance(data, dict):
        for key in ("msg", "message", "error", "stack"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return body[:300]


def _is_success(payload: Dict[str, Any]) -> bool:
    """
    Compatible with both styles:
    - code/status == 0
    - code/status == 200
    """
    if not isinstance(payload, dict):
        return False
    code = payload.get("code")
    status = payload.get("status")
    ok_code = code in (0, 200, "0", "200", None)
    ok_status = status in (0, 200, "0", "200", None)
    return ok_code and ok_status and isinstance(payload.get("data"), list)


def _http_call_compare(question: str) -> Dict[str, Any]:
    req_body = json.dumps({"question": question}, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        url=COMPARE_API_URL,
        method="POST",
        data=req_body,
        headers={
            "Content-Type": "application/json",
            "em_api_key": EM_API_KEY,
        },
    )

    try:
        with urllib_request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            raw_body = resp.read().decode("utf-8", errors="replace")
    except urllib_error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        message = _extract_error_message(err_body) or "http status {0}".format(exc.code)
        raise RuntimeError("Comparable-company API request failed: {0}".format(message))
    except urllib_error.URLError as exc:
        raise RuntimeError("Comparable-company API request failed: {0}".format(exc.reason))

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError:
        raise RuntimeError("Comparable-company API returned invalid JSON response.")

    if isinstance(parsed, dict):
        return parsed
    return {"data": parsed}


def _pick_dict(data_list: List[Any], idx: int) -> Dict[str, Any]:
    if 0 <= idx < len(data_list) and isinstance(data_list[idx], dict):
        return data_list[idx]
    return {}


async def fetch_comparable_company_data(question: str) -> Dict[str, Any]:
    question = (question or "").strip()
    if not question:
        return {
            "question": "",
            "header": {},
            "section_finance": {},
            "section_valuation": {},
            "records": [],
            "raw": None,
            "error": "question is empty",
        }

    result = {
        "question": question,
        "header": {},
        "section_finance": {},
        "section_valuation": {},
        "records": [],
        "raw": None,
    }

    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _http_call_compare, question)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["raw"] = raw
    if not _is_success(raw):
        message = ""
        if isinstance(raw, dict):
            msg_value = raw.get("message")
            if isinstance(msg_value, str):
                message = msg_value.strip()
        result["error"] = message or "API returned non-success status."
        return result

    data_list = raw.get("data")
    if not isinstance(data_list, list):
        result["error"] = "API data is not a list."
        return result

    result["records"] = data_list
    result["header"] = _pick_dict(data_list, 0)
    result["section_finance"] = _pick_dict(data_list, 1)
    result["section_valuation"] = _pick_dict(data_list, 2)
    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch comparable-company analysis data.")
    parser.add_argument("--query", type=str, help="Natural language company question.")
    return parser


def run_cli() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()
    query = (args.query or "").strip()
    if not query:
        import sys

        query = (sys.stdin.read() or "").strip()
    if not query:
        parser.print_help()
        raise SystemExit(1)

    async def _main() -> None:
        result = await fetch_comparable_company_data(question=query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if "error" in result:
            raise SystemExit(2)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()
