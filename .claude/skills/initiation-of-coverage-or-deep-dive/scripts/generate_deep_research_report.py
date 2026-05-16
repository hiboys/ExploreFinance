# -*- coding: utf-8 -*-
"""
首次覆盖报告 / 深度研究报告生成脚本。

调用首次覆盖写作接口，传入用户问句，生成完整报告并保存 PDF / Word 附件。
实体识别已内置在首次覆盖写作接口中，无需额外调用。

"""

import argparse
import asyncio
import base64
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict
import httpx

EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip()
# ─────────────────────────── 配置 ───────────────────────────

FIRST_COVERAGE_URL = (
    "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/write/initial-coverage"
)

DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "initiation_of_coverage_or_deep_dive"

REPORT_TIMEOUT = 1200.0


# ─────────────────── 调用首次覆盖写作接口 ───────────────────


def _save_base64_file(b64_str: str, file_path: Path) -> bool:
    """将 base64 字符串解码后写入文件。"""
    if not b64_str:
        return False
    try:
        raw = base64.b64decode(b64_str)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(raw)
        return True
    except Exception as exc:
        print(f"[WARN] 保存附件失败 ({file_path.name}): {exc}", file=sys.stderr)
        return False


async def generate_report(query: str, output_dir: Path) -> Dict:
    """
    调用首次覆盖写作接口生成报告，并将 PDF / Word 附件保存到本地。

    Returns:
        始终包含 query / pdf_file_path / word_file_path 三个字段；
        成功时额外含 title, content 等；失败时额外含 error。
    """
    result_base: Dict[str, Any] = {
        "query": query,
        "pdf_file_path": None,
        "word_file_path": None,
    }

    try:
        async with httpx.AsyncClient(timeout=REPORT_TIMEOUT, follow_redirects=True) as client:
            resp = await client.post(
                FIRST_COVERAGE_URL,
                json={"query": query},
                headers={
                    "Content-Type": "application/json",
                    "em_api_key": EM_API_KEY,
                },
            )
            resp.raise_for_status()
            payload = resp.json()
    except httpx.TimeoutException:
        return {**result_base, "error": "报告生成服务暂时不可用，请稍后重试。"}
    except httpx.HTTPStatusError as exc:
        return {
            **result_base,
            "error": f"报告生成服务返回异常状态码 {exc.response.status_code}，请稍后重试。",
        }
    except Exception as exc:
        return {**result_base, "error": f"报告生成服务暂时不可用，请稍后重试。（{exc}）"}

    code = payload.get("code")
    if code != 200:
        return {**result_base, "error": payload.get("message", "报告生成失败")}

    data = payload.get("data")
    if not data or not isinstance(data, dict):
        return {**result_base, "error": payload.get("message", "报告生成失败，返回数据为空")}

    output_dir.mkdir(parents=True, exist_ok=True)
    unique_suffix = uuid.uuid4().hex[:8]

    result: Dict[str, Any] = {
        "query": query,
        "pdf_file_path": None,
        "word_file_path": None,
        "articleId": data.get("articleId", ""),
        "title": data.get("title", ""),
        "content": data.get("content", ""),
        "shareUrl": data.get("shareUrl", ""),
        "refIndexList": data.get("refIndexList", []),
    }

    pdf_b64 = data.get("pdfBase64", "")
    if pdf_b64:
        pdf_path = output_dir / f"initiation_of_coverage_or_deep_dive_{unique_suffix}.pdf"
        if _save_base64_file(pdf_b64, pdf_path):
            result["pdf_file_path"] = str(pdf_path)

    word_b64 = data.get("wordBase64", "")
    if word_b64:
        word_path = output_dir / f"initiation_of_coverage_or_deep_dive_{unique_suffix}.docx"
        if _save_base64_file(word_b64, word_path):
            result["word_file_path"] = str(word_path)
    
    return result


# ─────────────────── CLI 入口 ───────────────────


def run_cli() -> None:
    """命令行入口：接收用户原始问句，执行完整流程并输出 JSON 结果。"""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="首次覆盖报告 / 深度研究报告生成"
    )
    parser.add_argument("--query", type=str, default="", help="用户原始问句")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="附件保存目录（默认 miaoxiang/initiation_of_coverage_or_deep_dive）",
    )
    args = parser.parse_args()

    if not args.query.strip():
        print("错误: 请提供查询内容", file=sys.stderr)
        sys.exit(1)

    env_output_dir = os.environ.get("INITIATION_OF_COVERAGE_OR_DEEP_DIVE_OUTPUT_DIR", "").strip()
    output_dir = Path(args.output_dir) if args.output_dir else (Path(env_output_dir) if env_output_dir else DEFAULT_OUTPUT_DIR)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            generate_report(args.query.strip(), output_dir)
        )
    finally:
        loop.close()

    if "error" in result:
        print(f"错误: {result['error']}", file=sys.stderr)
        sys.exit(2)

    # stdout must be a single JSON object for the skill contract
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    run_cli()
