"""
OpenClaw stock_diagnosis skill runtime.

This module is intentionally self-contained:
- No hard-coded user identity.
- Runtime defaults are defined in-code.
"""

import argparse
import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
from urllib import error as urllib_error
from urllib import request as urllib_request
EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "stock_diagnosis"
TIMEOUT_SECONDS = 60
STOCK_ANALYSIS_URL = (
    "https://ai-saas.eastmoney.com/proxy/"
    "app-robo-advisor-api/assistant/stock-analysis"
)


def _extract_error_message(body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    try:
        data = json.loads(body)
    except Exception:
        return body[:200]
    if isinstance(data, dict):
        for key in ("msg", "message", "error", "stack"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return body[:200]


def _extract_content(raw: Dict[str, Any]) -> str:
    """
    Extract readable report content from API response.
    Supports:
    - data.displayData as str
    - data.displayData as list/dict
    - fallback to common textual fields
    """
    if not isinstance(raw, dict):
        return ""

    data = raw.get("data")
    if isinstance(data, dict):
        display_data = data.get("displayData")
        if isinstance(display_data, str) and display_data.strip():
            return display_data.strip()
        if isinstance(display_data, (list, dict)):
            return json.dumps(display_data, ensure_ascii=False, indent=2)

        for key in ("content", "answer", "summary"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, (list, dict)):
                return json.dumps(value, ensure_ascii=False, indent=2)

    for key in ("displayData", "content", "answer", "summary"):
        value = raw.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(value, (list, dict)):
            return json.dumps(value, ensure_ascii=False, indent=2)

    return json.dumps(raw, ensure_ascii=False, indent=2)


def _http_call_stock_analysis(question: str) -> Dict[str, Any]:
    payload = {"question": question}
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib_request.Request(
        url=STOCK_ANALYSIS_URL,
        data=body,
        method="POST",
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
        message = _extract_error_message(err_body) or f"http status {exc.code}"
        raise RuntimeError(f"Stock analysis API request failed: {message}") from exc
    except urllib_error.URLError as exc:
        raise RuntimeError(f"Stock analysis API request failed: {exc.reason}") from exc

    try:
        parsed = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Stock analysis API returned invalid JSON response.") from exc

    if isinstance(parsed, dict):
        return parsed
    return {"data": parsed}


def _has_valid_display_data(raw: Dict[str, Any]) -> bool:
    """
    Determine whether API response contains a valid report body.
    Used to avoid saving md files for unsupported/failed scenarios.
    """
    if not isinstance(raw, dict):
        return False

    code = raw.get("code")
    if code is not None and code != 200:
        return False

    status = raw.get("status")
    if isinstance(status, int) and status < 0:
        return False

    data = raw.get("data")
    if not isinstance(data, dict):
        return False

    display_data = data.get("displayData")
    if isinstance(display_data, str):
        return bool(display_data.strip())
    if isinstance(display_data, list):
        return len(display_data) > 0
    if isinstance(display_data, dict):
        return len(display_data) > 0

    return False


async def diagnose_stock(
    question: str,
    output_dir: Optional[Path] = None,
    save_to_file: bool = True,
) -> Dict[str, Any]:
    question = (question or "").strip()
    if not question:
        return {
            "question": "",
            "content": "",
            "output_path": None,
            "raw": None,
            "error": "question is empty",
        }

    out_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "question": question,
        "content": "",
        "output_path": None,
        "raw": None,
    }

    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _http_call_stock_analysis, question)
    except Exception as exc:
        result["error"] = str(exc)
        return result

    result["raw"] = raw
    result["content"] = _extract_content(raw)

    if save_to_file and result["content"] and _has_valid_display_data(raw):
        unique_suffix = uuid.uuid4().hex[:8]
        output_path = out_dir / f"stock_diagnosis_{unique_suffix}.md"
        output_path.write_text(result["content"], encoding="utf-8")
        result["output_path"] = str(output_path)

    return result


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Diagnose one A-share stock from natural language question."
    )
    parser.add_argument("--query",type=str,help="Natural language stock question.")
    parser.add_argument("--no-save", action="store_true", help="Do not save result to local file.")
    return parser


def run_cli() -> None:
    parser = _build_arg_parser()
    args = parser.parse_args()

    question = (args.query or "").strip()
    if not question:
        import sys

        question = (sys.stdin.read() or "").strip()

    if not question:
        parser.print_help()
        raise SystemExit(1)

    async def _main() -> None:
        result = await diagnose_stock(question=question, save_to_file=not args.no_save)
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
