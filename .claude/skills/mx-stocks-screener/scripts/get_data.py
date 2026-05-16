"""
选股/选板块/选基金：通过 MCP 股票基金筛选获取数据，转为中文列名的 CSV 与描述文件。

支持 A股、港股、美股选股，以及选板块、选基金、选ETF、选可转债；
返回英文列名替换为中文后输出完整数据的 CSV 及数据说明。

"""

import asyncio
import csv
import json
import os
import re
import uuid
from pathlib import Path
from typing import List, Dict
import httpx


EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()


TOOL_NAME = "股票基金筛选"
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "mx_stocks_screener"
print('默认输出目录为：',DEFAULT_OUTPUT_DIR.absolute())
# MCP 服务器地址
MCP_URL = "https://ai-saas.eastmoney.com/proxy/b/mcp/tool/selectSecurity"


def get_metadata(
        query: str = "",
        selectType: str = "",
) -> dict:
    """
    生成 MCP 调用所需的 meta_data 字典

    Args:
        query: 查询文本

    Returns:
        包含完整 meta 信息的字典
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
def _build_column_map(columns: List[Dict]) -> Dict:
    """
    从 MCP 返回的 columns 构建 英文列名 -> 中文列名 的映射。
    支持常见字段名：field/name/key -> displayName/title/label。
    """
    name_map = {}
    for col in columns or []:
        if not isinstance(col, Dict):
            continue
        en_key = col.get("field", "") or col.get("name", "") or col.get("key", "")
        cn_name = col.get("displayName", "") or col.get("title", "") or col.get("label", "")
        cn_name = cn_name + ' ' + col.get('dateMsg') if col.get('dateMsg') else cn_name
        if en_key is not None and cn_name is not None:
            name_map[str(en_key)] = str(cn_name)
    return name_map


def _columns_order(columns: List[Dict]) -> List[str]:
    """按 columns 顺序返回英文列名列表，用于 CSV 表头顺序。"""
    order = []
    for col in columns or []:
        if not isinstance(col, Dict):
            continue
        en_key = col.get("field") or col.get("name") or col.get("key")
        if en_key is not None:
            order.append(str(en_key))
    return order


def _parse_partial_results_table(partial_results: str) -> List[Dict]:
    """
    将 partialResults 的 Markdown 表格字符串解析为行字典列表。
    格式: "|序号|代码|名称|...|\\n|---|\\n|1|000001|平安银行|...|"
    """
    if not partial_results or not isinstance(partial_results, str):
        return []
    lines = [ln.strip() for ln in partial_results.strip().splitlines() if ln.strip()]
    if not lines:
        return []

    # 表头行：按 | 分割，去掉首尾空
    def split_cells(line: str) -> List[str]:
        return [c.strip() for c in line.split("|") if c.strip() != ""]

    header_cells = split_cells(lines[0])
    if not header_cells:
        return []
    # 跳过分隔行（如 |---|---|）
    data_start = 1
    if data_start < len(lines) and re.match(r"^[\s\|\-]+$", lines[data_start]):
        data_start = 2
    rows = []
    for i in range(data_start, len(lines)):
        cells = split_cells(lines[i])
        if len(cells) != len(header_cells):
            # 列数不一致时按长度对齐，缺的补空
            if len(cells) < len(header_cells):
                cells.extend([""] * (len(header_cells) - len(cells)))
            else:
                cells = cells[: len(header_cells)]
        rows.append(dict(zip(header_cells, cells)))
    return rows


def _datalist_to_rows(
        datalist: List[Dict],
        column_map: Dict,
        column_order: List[str],
) -> List[Dict]:
    """
    将 datalist 中每行的英文键按 column_map 替换为中文键，保证顺序与 partialResults 风格一致。
    覆盖全部 datalist 数据。
    """
    if not datalist:
        return []

    rows = []
    for row in datalist:
        if not isinstance(row, Dict):
            continue
        cn_row = {}
        for en_key in column_order:
            if en_key not in row:
                continue
            cn_name = column_map.get(en_key, en_key)
            val = row[en_key]
            if val is None:
                cn_row[cn_name] = ""
            elif isinstance(val, (Dict, List)):
                cn_row[cn_name] = json.dumps(val, ensure_ascii=False)
            else:
                cn_row[cn_name] = str(val)
        rows.append(cn_row)

    return rows


def _drop_columns_for_sector(rows: List[Dict], select_type: str) -> List[Dict]:
    """
    当选择类型为“板块”时，移除不需要输出的列。
    目前按需求移除：
    - 板块编码
    - 指数内码
    """
    if select_type != "板块" or not rows:
        return rows

    blocked = {"板块编码", "指数内码"}
    cleaned_rows = []
    for row in rows:
        if not isinstance(row, Dict):
            continue
        cleaned_row = {
            k: v
            for k, v in row.items()
            if str(k).strip() not in blocked
        }
        cleaned_rows.append(cleaned_row)
    return cleaned_rows


async def query_mx_stocks_screener(
        query: str,
        selectType: str,
        output_dir: Path
) -> Dict:
    """
    通过自然语言查询进行选股（A股/港股/美股）、选板块、选基金；
    使用 MCP 股票基金筛选工具，将返回的 datalist 按 columns 转为中文列名 CSV 并生成描述文件。

    Args:
        query: 自然语言查询，如「股价大于1000元的股票」「港股科技龙头」「新能源板块」「白酒主题基金」
        selectType: 选股指定标的类型，格式：A股、港股、美股、基金、ETF、可转债、板块
        output_dir: 保存 CSV 和描述文件的目录；默认 workspace/mx_stocks_screener

    Returns:
        包含 csv_path, description_path, row_count, query，selectType；若失败则含 error。
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    result = {
        "csv_path": None,
        "description_path": None,
        "row_count": 0,
        "query": query,
        "selectType": selectType
    }

    try:
        raw = await mcp_single_call_v2(
            {"query": query, "selectType": selectType},
        )
    except Exception as e:
        result["error"] = f"MCP 调用失败: {e!s}"
        return result

    if not raw or not isinstance(raw, Dict):
        result["error"] = "MCP 返回为空或非 JSON 对象"
        result["raw_preview"] = str(raw)[:500] if raw else ""
        return result

    # 若 MCP 返回了非空 message，优先透传该错误信息
    raw_message = raw.get("message")
    if isinstance(raw_message, str) and raw_message.strip():
        result["error"] = raw_message.strip()+"\n您的请求数据量已达到上限，如需继续使用，请联系客服电话400-620-1818"
        return result

    # 使用 datalist（全量），兼容 allResults/result 为 None 的场景
    all_results = raw.get("allResults")
    if not isinstance(all_results, dict):
        all_results = {}
    result_node = all_results.get("result")
    if not isinstance(result_node, dict):
        result_node = {}

    # 若无 datalist 则回退到解析 partialResults 表格字符串
    dataList = result_node.get("dataList", [])
    if not isinstance(dataList, list):
        dataList = []

    columns = result_node.get("columns", [])
    if not isinstance(columns, list):
        columns = []

    rows = []
    data_source = ""

    if dataList:
        column_map = _build_column_map(columns)
        column_order = _columns_order(columns)
        rows = _datalist_to_rows(dataList, column_map, column_order)
        data_source = "dataList"

    if not rows:
        partial_results = raw.get("partialResults")
        if partial_results:
            rows = _parse_partial_results_table(partial_results)
            data_source = "partialResults"

    if not rows:
        if raw.get("securityCount", -1) == 0:
            result["error"] = "无符合问句要求的"+selectType
        else:
            result["error"] = "返回中无有效 datalist 且 partialResults 无法解析或为空"
        return result

    rows = _drop_columns_for_sector(rows, selectType)
    if not rows:
        result["error"] = "过滤板块字段后无可输出数据"
        return result

    fieldnames = list(rows[0].keys())
    unique_suffix = uuid.uuid4().hex[:8]
    csv_path = output_dir / f"mx_stocks_screener_{unique_suffix}.csv"
    desc_path = output_dir / f"mx_stocks_screener_{unique_suffix}_description.txt"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    description_lines = [
        "选股/选板块/选基金 结果说明",
        "=" * 40,
        f"查询内容: {query}",
        f"数据行数: {len(rows)}（来源: {data_source}）",
        f"列名（中文）: {', '.join(fieldnames)}",
        "",
        "说明: 数据来源于 MCP 股票基金筛选；"
        + ("列名已按 columns 映射为中文。" if data_source == "dataList" else "表格来自 partialResults。"),
    ]
    desc_path.write_text("\n".join(description_lines), encoding="utf-8")

    result["csv_path"] = str(csv_path)
    result["description_path"] = str(desc_path)
    result["row_count"] = len(rows)
    return result


def run_cli() -> None:
    import argparse
    import sys
    """命令行入口：从参数或 stdin 读取查询文本，执行并打印结果路径。"""

    parser = argparse.ArgumentParser(description='通过自然语言查询进行选股、选板块、选基金')

    # 添加query参数
    parser.add_argument('--query', type=str, help='自然语言查询，如「股价大于1000元的股票」', required=True)

    # 添加选股类型参数
    parser.add_argument('--select-type', dest='selectType',
                        choices=['A股', '港股', '美股', '基金', 'ETF', '可转债', '板块'],
                        help='选股指定标的类型', required=True)
    args = parser.parse_args()

    print(f"Query: {args.query}，SelectType: {args.selectType}")

    if not args.query:
        print("用法: python -m scripts.get_data --query \"查询文本\" --select-type \"查询领域\"")
        print("示例: 股价大于1000元的股票 / 港股科技龙头 / 新能源板块 / 白酒主题基金")
        sys.exit(1)

    async def _main() -> None:
        out_dir = Path(os.environ.get("MX_STOCKS_SCREENER_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
        r = await query_mx_stocks_screener(args.query, args.selectType, output_dir=out_dir)
        if "error" in r:
            print(f"错误: {r['error']}", file=sys.stderr)
            if "raw_preview" in r:
                print(r["raw_preview"], file=sys.stderr)
            sys.exit(2)
        print(f"CSV: {r['csv_path']}")
        print(f"描述: {r['description_path']}")
        print(f"行数: {r['row_count']}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.close()


# MCP 调用函数
async def mcp_single_call_v2(arguments):
    """MCP 异步调用函数"""

    query = arguments.get("query", "")
    selectType = arguments.get("selectType", "")
    meta = get_metadata(query=query, selectType=selectType)
    result_data = {}

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await client.post(
                MCP_URL,
                json=meta,
                headers={
                    "Content-Type": "application/json",
                    "em_api_key": EM_API_KEY,
                },
            )
            try:
                payload = result.json()
            except Exception as e:
                print(f"响应体 JSON 解析失败: {e}")
                return result_data

            if isinstance(payload, dict):
                result_data = payload.get("data") or {}
            else:
                print(f"响应 JSON 顶层不是对象，类型: {type(payload).__name__}")
                return result_data

            if result_data:
                print("调用成功！")
                return result_data
            else:
                print("------------  返回结果格式未解析成功  ------------")
                print(f"顶层字段: {list(payload.keys()) if isinstance(payload, dict) else 'N/A'}")
                return result_data

    except Exception as e:
        print(f"调用工具时出错: {e}")
        import traceback
        traceback.print_exc()
        return result_data


if __name__ == "__main__":
    run_cli()