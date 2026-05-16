import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict

import httpx

from common import (
    PERFORMANCE_COMMENT_API,
    EntityInfo,
    build_comment_payload,
    extract_comment_response_fields,
    ensure_log_dir,
    save_attachment_payload,
    write_json_log,
    base_headers,
)


async def call_review_api(
    entity: EntityInfo,
    report_date: str,
    log_dir: str = "",
    attachment_dir: str = "",
    debug: bool = False
) -> Dict[str, Any]:
    payload = build_comment_payload(entity.em_code, report_date)
    async with httpx.AsyncClient(timeout=1200.0, verify=True) as client:
        resp = await client.post(PERFORMANCE_COMMENT_API, headers=base_headers(), json=payload)
        resp.raise_for_status()
        raw = resp.json()

    code = raw.get("code") if isinstance(raw, dict) else None
    status = raw.get("status") if isinstance(raw, dict) else None
    if code not in (0, 200) or status not in (0, 200):
        raise RuntimeError(f"业绩点评接口返回异常: code={code}, status={status}, message={raw.get('message') if isinstance(raw, dict) else ''}")

    # 仅 debug 时写阶段 JSON 日志；附件保存不受 debug 影响
    log_path = None
    if log_dir:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
    elif debug:
        log_path = ensure_log_dir(None)
    if debug and log_path:
        write_json_log(log_path, "03_comment_raw.json", raw)
    parsed = extract_comment_response_fields(raw)
    title = str(parsed.get("title") or "")
    content = str(parsed.get("content") or "")

    attachment_candidates: Dict[str, Any] = {
        "pdfBase64": {"base64": parsed.get("pdfBase64") or "", "filename": "review.pdf"},
        "wordBase64": {"base64": parsed.get("wordBase64") or "", "filename": "review.doc"},
    }
    ds_b64 = parsed.get("dataSheetBase64")
    if ds_b64:
        attachment_candidates["dataSheetBase64"] = {"base64": ds_b64, "filename": "review_data.xlsx"}
    saved_attachments: Dict[str, str] = {}
    if attachment_dir:
        output_attachment_dir = attachment_dir
    elif log_path:
        output_attachment_dir = str(log_path / "attachments")
    else:
        output_attachment_dir = str(ensure_log_dir(None) / "attachments")
    for name, payload in attachment_candidates.items():
        if isinstance(payload, dict):
            saved = save_attachment_payload(payload, output_attachment_dir, f"{name}.bin")
            if saved:
                saved_attachments[name] = saved

    result = {
        "title": title,
        "content": content,
        "shareUrl": parsed.get("shareUrl"),
        "files": {
            "pdf": saved_attachments.get("pdfBase64"),
            "word": saved_attachments.get("wordBase64"),
            "dataSheet": saved_attachments.get("dataSheetBase64"),
        },
    }
    if debug:
        result["raw"] = raw
    if debug and log_path:
        write_json_log(log_path, "04_review_result.json", result)
        result["logDir"] = str(log_path)
    return result


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Call earnings review performance comment API.")
    parser.add_argument("--secu-code", required=True)
    parser.add_argument("--market-char", required=True)
    parser.add_argument("--class-code", required=True)
    parser.add_argument("--report-date", required=True)
    parser.add_argument("--secu-name", default="")
    parser.add_argument("--log-dir", default="")
    parser.add_argument("--attachment-dir", default="")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    async def _main() -> None:
        entity = EntityInfo(
            class_code=args.class_code,
            secu_code=args.secu_code,
            market_char=args.market_char,
            secu_name=args.secu_name,
        )
        result = await call_review_api(
            entity,
            args.report_date,
            log_dir=args.log_dir,
            attachment_dir=args.attachment_dir,
            debug=args.debug,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()

