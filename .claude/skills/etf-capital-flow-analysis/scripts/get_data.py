"""
ETF Capital Flow Analysis skill runtime.

Self-contained script for automated ETF capital flow data fetching,
divergence analysis, and structured Markdown report generation.

This module is intentionally self-contained:
- No hard-coded user identity.
- Runtime defaults are defined in-code.
"""

import argparse
import asyncio
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
SEARCH_DATA_URL = "https://ai-saas.eastmoney.com/proxy/b/mcp/tool/searchData"
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "etf_capital_flow_analysis"
TIMEOUT_SECONDS = 60


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _flatten_value(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return str(v)


def _safe_float(raw: Any) -> Optional[float]:
    """Convert raw value to float, stripping commas / 亿元 / 万 等后缀."""
    if raw is None:
        return None
    s = str(raw).replace(",", "").replace("%", "").strip()
    # 亿元 → * 1e8
    yi_mult = 1.0
    if "亿" in s:
        yi_mult = 1e8
        s = s.replace("亿", "")
    elif "万" in s:
        yi_mult = 1e4
        s = s.replace("万", "")
    try:
        return float(s) * yi_mult
    except (ValueError, TypeError):
        return None


def _safe_int(raw: Any) -> Optional[int]:
    v = _safe_float(raw)
    return int(v) if v is not None else None


def _build_request_body(query: str) -> Dict[str, Any]:
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    return {
        "query": query,
        "toolContext": {
            "callId": call_id,
            "userInfo": {"userId": user_id},
        },
    }


# ---------------------------------------------------------------------------
# API communication
# ---------------------------------------------------------------------------

def _extract_data_table_dto_list(api_result: Any) -> Tuple[Optional[List[Any]], Optional[str]]:
    if not isinstance(api_result, dict):
        return None, "API response is not a JSON object"

    dto_list = api_result.get("dataTableDTOList")
    if isinstance(dto_list, list):
        return dto_list, None

    data_node = api_result.get("data")
    if isinstance(data_node, dict):
        search_result = data_node.get("searchDataResultDTO")
        if isinstance(search_result, dict):
            dto_list = search_result.get("dataTableDTOList")
            if isinstance(dto_list, list):
                return dto_list, None
        dto_list = data_node.get("dataTableDTOList")
        if isinstance(dto_list, list):
            return dto_list, None

    return None, "No dataTableDTOList found in API response"


def _check_business_status(api_result: Any) -> Optional[str]:
    if not isinstance(api_result, dict):
        return "API response is not a JSON object"
    code = api_result.get("code")
    status = api_result.get("status")
    success_values = (None, 0, 200, "0", "200")
    if code not in success_values or status not in success_values:
        message = _flatten_value(api_result.get("message") or "business status not success")
        return f"API business error: code={code}, status={status}, message={message}"
    return None


async def _call_search_data_api(query: str) -> Dict[str, Any]:
    """Call the searchData MCP endpoint and return parsed JSON."""
    body = _build_request_body(query)
    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            SEARCH_DATA_URL,
            json=body,
            headers={
                "Content-Type": "application/json",
                "em_api_key": EM_API_KEY,
            },
        )
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Utility: ETF name extraction from query
# ---------------------------------------------------------------------------

# Common ETF name patterns in Chinese market
_ETF_NAME_PATTERN = re.compile(
    r"(?:"
    r"[沪深京证]\w{0,3}\d{0,3}ETF|"         # 沪深300ETF, 科创50ETF
    r"\w+ETF|"                               # 通信ETF, 半导体ETF
    r"\d{6}"                                 # 510300, 159915
    r")"
)


def _extract_etf_names_from_query(query: str) -> List[str]:
    """Extract ETF names/codes from the natural language query."""
    matches = _ETF_NAME_PATTERN.findall(query)
    # Deduplicate while preserving order
    seen = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result if result else [query[:40]]


# ---------------------------------------------------------------------------
# Data parsing — extract ETF-level metrics from sheet rows
# ---------------------------------------------------------------------------

def _is_timestamp_header(h: str) -> bool:
    """Check if a header looks like a timestamp rather than a meaningful column name."""
    h = h.strip()
    # Match patterns like "2026-06-09 21:09", "2026-06-05", etc.
    if re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}", h):
        return True
    return False


def _parse_sheet_to_records(dto: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse a single dataTableDTO block into a list of row dicts.
    Handles the common headName + indicator key structure used by searchData.
    """
    table = dto.get("table") or {}
    if not isinstance(table, dict):
        return []

    name_map = dto.get("nameMap") or {}
    if isinstance(name_map, list):
        name_map = {str(i): v for i, v in enumerate(name_map)}
    elif not isinstance(name_map, dict):
        name_map = {}

    raw_headers = table.get("headName") or []
    if not isinstance(raw_headers, list) or not raw_headers:
        return []

    # Filter out timestamp headers (e.g. "2026-06-09 21:09")
    # and keep only meaningful column names
    headers = [h for h in raw_headers if not _is_timestamp_header(str(h))]
    if not headers:
        headers = raw_headers  # fallback if all filtered

    entity_name = _flatten_value(dto.get("entityName") or "指标")
    code_map: Dict[str, str] = {}
    for key in ("returnCodeMap", "returnCodeNameMap", "codeMap"):
        data = dto.get(key)
        if isinstance(data, dict):
            code_map = {str(k): _flatten_value(v) for k, v in data.items()}
            break

    rows: List[Dict[str, Any]] = []
    data_keys = [k for k in table.keys() if k != "headName"]

    for key in data_keys:
        raw_values = table.get(key, [])
        if not isinstance(raw_values, list):
            raw_values = [raw_values]
        values = [_flatten_value(v) for v in raw_values]
        if len(values) < len(headers):
            values.extend([""] * (len(headers) - len(values)))
        values = values[: len(headers)]

        label = name_map.get(str(key))
        if label is None and str(key).isdigit():
            label = name_map.get(int(key))
        if label is None:
            label = code_map.get(str(key))
        if label is None and str(key).isdigit():
            label = ""
        if label is None:
            label = str(key)

        row = {"指标": _flatten_value(label)}
        for i, h in enumerate(headers):
            row[_flatten_value(h)] = values[i]
        rows.append(row)

    return rows


def _extract_etf_metrics(dto_list: List[Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Walk through all sheets and extract ETF-level capital flow metrics.
    Returns (all_rows, etf_column_names).
    etf_column_names are the ETF-specific columns found in the cross-tab data.
    """
    all_rows: List[Dict[str, Any]] = []
    etf_columns: Set[str] = set()

    for dto in dto_list:
        if not isinstance(dto, dict):
            continue
        rows = _parse_sheet_to_records(dto)
        # Detect ETF columns from row keys
        for row in rows:
            for key in row.keys():
                if key == "指标":
                    continue
                # Column names like "华泰柏瑞沪深300ETF(510300.SH)" contain ETF identifiers
                if "ETF" in key or re.search(r"\(\d{6}\.", key):
                    etf_columns.add(key)
        all_rows.extend(rows)
    return all_rows, sorted(etf_columns)


# Known fund-company prefixes in Chinese ETF names (to strip for short names)
_FUND_COMPANY_PREFIXES = [
    "华泰柏瑞", "华夏", "易方达", "南方", "广发", "富国", "嘉实",
    "博时", "天弘", "国泰", "招商", "工银瑞信", "汇添富", "景顺长城",
    "鹏华", "华安", "银华", "万家", "中欧", "交银施罗德", "兴证全球",
    "国联安", "海富通", "建信", "民生加银", "大成", "平安",
]


def _derive_etf_short_name(col: str) -> str:
    """
    Derive a short, readable ETF name from a full column header.
    "华泰柏瑞沪深300ETF(510300.SH)" → "沪深300ETF(510300)"
    "华夏上证科创板50成份ETF(588000.SH)" → "科创50ETF(588000)"
    """
    # Extract 6-digit code
    code_m = re.search(r"\((\d{6})", col)
    code = code_m.group(1) if code_m else ""

    # Strip known fund company prefix
    name = col
    for prefix in _FUND_COMPANY_PREFIXES:
        if name.startswith(prefix):
            name = name[len(prefix):]
            break

    # Clean up: remove .SH/.SZ suffix from code, simplify "成份ETF" → "ETF"
    name = name.replace(".SH)", ")").replace(".SZ)", ")")
    name = name.replace("成份ETF", "ETF")

    if code and code not in name:
        name = f"{name}({code})" if "(" not in name else re.sub(r"\(\d{6}[^)]*\)", f"({code})", name)

    return name if name else col


def _pivot_to_per_etf_rows(
    all_rows: List[Dict[str, Any]],
    etf_columns: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Pivot cross-tab data (ETF x Indicator) into per-ETF row groups.
    Returns {etf_short_name: [{"指标": ..., "值": ...}, ...]}
    """
    result: Dict[str, List[Dict[str, Any]]] = {}

    for col in etf_columns:
        short_name = _derive_etf_short_name(col)

        etf_rows: List[Dict[str, Any]] = []
        for row in all_rows:
            indicator = row.get("指标", "")
            value = row.get(col, "")
            if value:
                etf_rows.append({"指标": indicator, "值": str(value)})
        if etf_rows:
            result[short_name] = etf_rows

    return result


# ---------------------------------------------------------------------------
# Analysis: divergence detection
# ---------------------------------------------------------------------------

def _find_value(rows: List[Dict[str, Any]], keywords: List[str]) -> Optional[str]:
    """Find a row whose 指标 column contains any of the given keywords.
    Returns the value from the column that looks most like a numeric/amount value
    (skipping DDX/DDY/DDZ and other technical indicator columns)."""
    for row in rows:
        indicator = str(row.get("指标", ""))
        if any(kw in indicator for kw in keywords):
            # Find the best value column — prefer columns with 亿/万/元/%
            # Skip technical indicators like DDX, DDY, DDZ
            best_val = None
            for k, v in row.items():
                if k == "指标":
                    continue
                vs = str(v).strip()
                if not vs:
                    continue
                # Skip DDX/DDY/DDZ technical columns
                if any(skip in str(k) for skip in ("DDX", "DDY", "DDZ")):
                    continue
                # Prefer columns with unit markers (亿/万/元/%)
                if any(unit in vs for unit in ("亿", "万", "元", "%")):
                    return vs
                if best_val is None:
                    best_val = vs
            if best_val:
                return best_val
    return None


def _analyze_flows(
    etf_rows: List[Dict[str, Any]],
    etf_name: str,
) -> Dict[str, Any]:
    """
    Analyse capital flow signals for a single ETF.
    Returns structured signal dict.
    """
    result: Dict[str, Any] = {
        "name": etf_name,
        "market_cap": _find_value(etf_rows, ["总市值", "市值", "规模", "基金规模"]),
        "weekly_return": _find_value(etf_rows, ["涨跌幅", "近一周涨跌幅", "区间涨跌幅"]),
        "main_force_5d": _find_value(etf_rows, [
            "主力净流入资金", "主力净流入", "5日主力净流入",
            "主力资金净流入", "主力净额",
        ]),
        "net_subscription_5d": _find_value(etf_rows, [
            "净申购额", "净申购", "申购赎回净额",
            "净申赎", "申购赎回", "净赎回",
        ]),
        "daily_flows": [],  # list of {date, main_force, subscription}
        "divergence_signal": None,
        "risk_level": None,
    }

    # Detect divergence
    mf_str = result["main_force_5d"]
    ns_str = result["net_subscription_5d"]

    mf_val = _safe_float(mf_str)
    ns_val = _safe_float(ns_str)

    if mf_val is not None and ns_val is not None:
        if mf_val > 0 and ns_val < 0:
            result["divergence_signal"] = "主力买、份额赎 — 短期博弈资金为主，非长期配置"
            result["risk_level"] = "🟡 关注"
        elif mf_val < 0 and ns_val > 0:
            result["divergence_signal"] = "⚠️ 主力卖、份额申 — 拥挤度风险，主力高位派发"
            result["risk_level"] = "🔴 高风险"
        elif mf_val > 0 and ns_val > 0:
            result["divergence_signal"] = "主力买、份额申 — 信号一致看多，资金真实流入"
            result["risk_level"] = "🟢 健康"
        elif mf_val < 0 and ns_val < 0:
            result["divergence_signal"] = "主力卖、份额赎 — 信号一致看空，资金真实流出"
            result["risk_level"] = "🔴 警惕"
        else:
            result["divergence_signal"] = "信号中性"
            result["risk_level"] = "—"

    return result


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _generate_markdown_report(
    query: str,
    etf_analyses: List[Dict[str, Any]],
    raw_rows: List[Dict[str, Any]],
) -> str:
    """Generate a structured Markdown report from ETF analysis results."""

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines: List[str] = []

    # Title
    lines.append(f"# ETF 资金流深度分析报告")
    lines.append(f"")
    lines.append(f"**查询**: {query}")
    lines.append(f"**生成时间**: {now_str}")
    lines.append(f"**分析 ETF 数量**: {len(etf_analyses)}")
    lines.append(f"")

    # ── Part 1: Summary Table ──
    lines.append(f"## 一、全景汇总表")
    lines.append(f"")
    header = "| ETF | 市值 | 近一周涨跌幅 | 5日主力净流入 | 5日净申购额 | 分歧信号 |"
    sep = "|---|---|---|---|---|---|"
    lines.append(header)
    lines.append(sep)
    for a in etf_analyses:
        lines.append(
            f"| {a['name']} "
            f"| {a.get('market_cap') or '—'} "
            f"| {a.get('weekly_return') or '—'} "
            f"| {a.get('main_force_5d') or '—'} "
            f"| {a.get('net_subscription_5d') or '—'} "
            f"| {a.get('risk_level') or '—'} |"
        )
    lines.append(f"")

    # ── Part 2: Key Findings ──
    lines.append(f"## 二、关键发现")
    lines.append(f"")

    # Sort by risk
    high_risk = [a for a in etf_analyses if "🔴" in (a.get("risk_level") or "")]
    watch = [a for a in etf_analyses if "🟡" in (a.get("risk_level") or "")]
    healthy = [a for a in etf_analyses if "🟢" in (a.get("risk_level") or "")]

    if high_risk:
        lines.append(f"### 🔴 高风险信号")
        for a in high_risk:
            lines.append(f"- **{a['name']}**: {a.get('divergence_signal', '—')}")
        lines.append(f"")

    if watch:
        lines.append(f"### 🟡 关注信号")
        for a in watch:
            lines.append(f"- **{a['name']}**: {a.get('divergence_signal', '—')}")
        lines.append(f"")

    if healthy:
        lines.append(f"### 🟢 健康信号")
        for a in healthy:
            lines.append(f"- **{a['name']}**: {a.get('divergence_signal', '—')}")
        lines.append(f"")

    # ── Part 3: Divergence Detail ──
    lines.append(f"## 三、🔥 核心分歧深度分析")
    lines.append(f"")
    lines.append(f"> 主力净流入 vs 净申购额的分歧是判断资金真实意图的关键指标。")
    lines.append(f"")

    has_divergence = False
    for a in etf_analyses:
        sig = a.get("divergence_signal")
        if sig and sig not in ("信号一致看多，资金真实流入", "信号一致看空，资金真实流出", "信号中性"):
            has_divergence = True
            lines.append(f"### {a['name']}")
            lines.append(f"")
            lines.append(f"- **主力净流入**: {a.get('main_force_5d') or '—'}")
            lines.append(f"- **净申购额**: {a.get('net_subscription_5d') or '—'}")
            lines.append(f"- **分歧类型**: {sig}")
            lines.append(f"- **风险等级**: {a.get('risk_level') or '—'}")
            lines.append(f"")

    if not has_divergence:
        lines.append(f"> 当前未检测到显著的主力-申购分歧信号。资金流向与申购赎回方向一致，信号可信度较高。")
        lines.append(f"")

    # ── Part 4: Actionable Checklist ──
    lines.append(f"## 四、综合判断与可执行清单")
    lines.append(f"")
    lines.append(f"| 优先级 | 判断 | ETF | 验证信号 |")
    lines.append(f"|---|---|---|---|")
    for a in etf_analyses:
        risk = a.get("risk_level") or "—"
        if "🔴" in risk:
            lines.append(f"| 🔴 高 | 拥堵风险 / 顶部信号 | {a['name']} | 主力连续净流出 + 净申购为正 |")
        elif "🟡" in risk:
            lines.append(f"| 🟡 中 | 趋势持续 / 反转观察 | {a['name']} | 净流入是否连续3日同向 |")
        elif "🟢" in risk:
            lines.append(f"| 🟢 低 | 板块企稳 / 筑底 | {a['name']} | 等待资金回流信号 |")
        else:
            lines.append(f"| — | 待判断 | {a['name']} | 需更多数据 |")
    lines.append(f"")

    # ── Part 5: Raw Data Appendix ──
    lines.append(f"## 五、原始数据附录")
    lines.append(f"")
    if raw_rows:
        # Show first 30 rows max
        rows_to_show = raw_rows[:30]
        cols = set()
        for r in rows_to_show:
            cols.update(r.keys())
        cols = sorted(cols)
        lines.append("| " + " | ".join(cols) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")
        for r in rows_to_show:
            lines.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
        if len(raw_rows) > 30:
            lines.append(f"")
            lines.append(f"> *仅展示前 30 行，共 {len(raw_rows)} 行原始数据*")
    else:
        lines.append("> 无原始数据返回")
    lines.append(f"")

    # ── Disclaimer ──
    lines.append(f"---")
    lines.append(f"")
    lines.append(f"**风险提示**: 本报告基于东方财富数据接口自动生成，资金流数据存在延迟。分析结果仅供参考，不构成投资建议。过往资金流向不代表未来走势。")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------------

async def analyze_etf_capital_flow(
    query: str,
    output_dir: Optional[Path] = None,
    save_to_file: bool = True,
) -> Dict[str, Any]:
    """
    Execute full ETF capital flow analysis workflow:
    1. Query searchData API
    2. Parse response into structured records
    3. Run divergence analysis
    4. Generate Markdown report
    5. Save report to file
    """
    query = (query or "").strip()
    if not query:
        return {
            "query": "",
            "content": "",
            "output_path": None,
            "error": "query is empty",
        }

    out_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    result: Dict[str, Any] = {
        "query": query,
        "content": "",
        "output_path": None,
        "raw": None,
    }

    # Step 1: Call API
    try:
        api_result = await _call_search_data_api(query)
        result["raw"] = api_result
    except Exception as exc:
        result["error"] = f"API request failed: {exc!s}"
        return result

    # Step 2: Business status check
    status_err = _check_business_status(api_result)
    if status_err:
        result["error"] = status_err
        return result

    # Step 3: Extract data
    dto_list, extract_err = _extract_data_table_dto_list(api_result)
    if extract_err:
        result["error"] = extract_err
        return result
    if not dto_list:
        result["error"] = "API returned empty dataTableDTOList"
        return result

    # Step 4: Parse rows and identify ETF columns
    all_rows, etf_columns = _extract_etf_metrics(dto_list)
    if not all_rows:
        result["error"] = "No parseable data rows found in API response"
        return result

    # Step 5: Pivot cross-tab data into per-ETF groups and analyse
    if etf_columns:
        # Multi-ETF cross-tab: pivot into per-ETF row groups
        etf_groups = _pivot_to_per_etf_rows(all_rows, etf_columns)
    else:
        # Single ETF or simple format: use query-extracted names
        etf_names = _extract_etf_names_from_query(query)
        etf_groups = {name: all_rows for name in etf_names}

    etf_analyses = []
    for etf_name, etf_rows in etf_groups.items():
        analysis = _analyze_flows(etf_rows, etf_name)
        etf_analyses.append(analysis)

    # Step 7: Generate report
    report_content = _generate_markdown_report(query, etf_analyses, all_rows)
    result["content"] = report_content

    # Step 8: Save file
    if save_to_file and report_content:
        unique_suffix = uuid.uuid4().hex[:8]
        output_path = out_dir / f"etf_capital_flow_{unique_suffix}.md"
        output_path.write_text(report_content, encoding="utf-8")
        result["output_path"] = str(output_path)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ETF capital flow analysis — fetch data, detect divergence, generate report."
    )
    parser.add_argument(
        "--query", type=str,
        help="Natural language query for ETF capital flow data (e.g. 沪深300ETF 近一周资金流向)."
    )
    parser.add_argument(
        "--no-save", action="store_true",
        help="Do not save report to local file."
    )
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
        result = await analyze_etf_capital_flow(
            query=question,
            save_to_file=not args.no_save,
        )
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
