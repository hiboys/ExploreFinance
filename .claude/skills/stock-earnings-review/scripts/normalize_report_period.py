import argparse
import asyncio
import json
from dataclasses import dataclass
from typing import Any, List, Optional

import httpx

from common import REPORT_LIST_API, EntityInfo, base_headers


@dataclass
class ReportOption:
    report_date: str
    period_label: str = ""
    raw: Any = None


async def fetch_report_options(entity: EntityInfo) -> List[ReportOption]:
    async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
        resp = await client.post(REPORT_LIST_API, headers=base_headers(), json={"emCode": entity.em_code})
        resp.raise_for_status()
        raw = resp.json()

    code = raw.get("code") if isinstance(raw, dict) else None
    status = raw.get("status") if isinstance(raw, dict) else None
    if code not in (0, 200) or status not in (0, 200):
        raise RuntimeError(f"报告期接口返回异常: code={code}, status={status}, message={raw.get('message') if isinstance(raw, dict) else ''}")

    data = raw.get("data") if isinstance(raw, dict) and isinstance(raw.get("data"), dict) else {}
    # actual response field verified by test: reportDateList
    src = data.get("reportDateList", []) if isinstance(data, dict) else []
    if not isinstance(src, list) or not src:
        raise RuntimeError("报告期列表获取失败或为空")

    out: List[ReportOption] = []
    for item in src:
        if isinstance(item, str):
            out.append(ReportOption(report_date=item, raw=item))
        elif isinstance(item, dict):
            report_date = item.get("reportDate") or item.get("report_date") or item.get("date")
            if report_date:
                out.append(
                    ReportOption(
                        report_date=str(report_date),
                        period_label=str(item.get("period") or ""),
                        raw=item,
                    )
                )
    if not out:
        raise RuntimeError("报告期列表解析失败")
    return out


def choose_report_option_by_model(
    options: List[ReportOption],
    selected_report_date: Optional[str] = None,
    strict: bool = True,
) -> ReportOption:
    if not options:
        raise RuntimeError("暂无该实体的可用报告期数据")
    if selected_report_date:
        s = selected_report_date.strip()
        for opt in options:
            if opt.report_date == s:
                return opt
        if strict:
            raise RuntimeError(
                "selected_report_date 不在候选报告期中: "
                f"{s}; 可选值: {[o.report_date for o in options]}"
            )
    return options[0]


def run_cli() -> None:
    parser = argparse.ArgumentParser(description="Fetch report period options and validate model selection.")
    parser.add_argument("--secu-code", required=True)
    parser.add_argument("--market-char", required=True)
    parser.add_argument("--class-code", required=True)
    parser.add_argument("--secu-name", default="")
    parser.add_argument("--selected-report-date", default="")
    parser.add_argument("--non-strict", action="store_true")
    args = parser.parse_args()

    async def _main() -> None:
        entity = EntityInfo(
            class_code=args.class_code,
            secu_code=args.secu_code,
            market_char=args.market_char,
            secu_name=args.secu_name,
        )
        options = await fetch_report_options(entity)
        matched = choose_report_option_by_model(
            options,
            args.selected_report_date or None,
            strict=not args.non_strict,
        )
        print(
            json.dumps(
                {
                    "entity": {
                        "classCode": entity.class_code,
                        "secuCode": entity.secu_code,
                        "marketChar": entity.market_char,
                        "secuName": entity.secu_name,
                        "emCode": entity.em_code,
                    },
                    "reportOptions": [
                        {"reportDate": o.report_date, "periodLabel": o.period_label}
                        for o in options
                    ],
                    "matchedReport": {
                        "reportDate": matched.report_date,
                        "periodLabel": matched.period_label,
                    },
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


if __name__ == "__main__":
    run_cli()

