import json
import os
import re
import uuid
import base64
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

ENTITY_API = "https://ai-saas.eastmoney.com/proxy/entity/dialogTagsV2"
REPORT_LIST_API = "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/write/choice/reportList"
PERFORMANCE_COMMENT_API = "https://ai-saas.eastmoney.com/proxy/app-robo-advisor-api/assistant/write/performance/comment"
SUPPORTED_CLASS_CODES = {"002001", "002003", "002004"}

# 默认写入当前工作目录下的 miaoxiang/<skill_slug>/
DEFAULT_OUTPUT_DIR = Path.cwd() / "miaoxiang" / "stock-earnings-review"


def default_output_root() -> Path:
    """
    单次执行日志与附件的根目录（其下再创建按 run_id 分组的子目录）。
    优先级：STOCK_EARNINGS_REVIEW_OUTPUT_DIR > DEFAULT_OUTPUT_DIR。
    """
    env = os.environ.get("STOCK_EARNINGS_REVIEW_OUTPUT_DIR") 
    if env:
        return Path(env)
    return DEFAULT_OUTPUT_DIR

_API_KEY_PLACEHOLDER = "<EM_API_KEY_PLACEHOLDER>"
EM_API_KEY = os.environ.get("EM_API_KEY", "em_IRn5yp1W8DOoWkqGK0KCr2VRsHia4JNZ").strip() or _API_KEY_PLACEHOLDER

@dataclass
class EntityInfo:
    class_code: str
    secu_code: str
    market_char: str
    secu_name: str = ""

    @property
    def em_code(self) -> str:
        if "." in self.secu_code:
            return self.secu_code
        suffix = (self.market_char or "").strip()
        if not suffix:
            raise RuntimeError("实体识别缺少 marketChar，无法拼接 emCode")
        if suffix and not suffix.startswith("."):
            suffix = f".{suffix}"
        return f"{self.secu_code}{suffix}"


def clean_header_value(name: str, value: str) -> str:
    cleaned = (value or "")
    for ch in ("\ufeff", "\u200b", "\u200c", "\u200d", "\u2060"):
        cleaned = cleaned.replace(ch, "")
    cleaned = cleaned.replace("\r", "").replace("\n", "").replace("\t", "").strip().strip("\"'“”‘’")
    if not cleaned:
        raise RuntimeError(f"{name} 未配置，请先设置环境变量")
    return cleaned


def auth_headers() -> Dict[str, str]:
    if EM_API_KEY == _API_KEY_PLACEHOLDER:
        raise RuntimeError("请先设置 EM_API_KEY 环境变量")
    return {
        "em_api_key": clean_header_value("EM_API_KEY", EM_API_KEY),
    }


def base_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "em_base_info": json.dumps({"productType": "mx"}, ensure_ascii=False, separators=(",", ":")),
        **auth_headers(),
    }


def build_comment_payload(em_code: str, report_date: str) -> Dict[str, str]:
    return {"query": em_code, "reportDate": report_date}


def extract_title(content: str) -> str:
    m = re.search(r"(?m)^##\s*(.+?)\s*$", content or "")
    if m:
        return m.group(1).strip()
    for line in (content or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def _pick_data_sheet_base64(data: Dict[str, Any]) -> Any:
    if not isinstance(data, dict):
        return None
    for k in (
        "dataSheetBase64",
        "excelBase64",
        "dataBase64",
        "sheetBase64",
        "dataBase64Str",
        "attachDataBase64",
    ):
        v = data.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return None


def attachment_local_status(saved_path: Optional[str]) -> Dict[str, Any]:
    """确认附件是否已写入本地：路径、是否存在、文件大小。"""
    if not saved_path:
        return {"path": None, "saved": False, "sizeBytes": None}
    p = Path(saved_path)
    try:
        if p.is_file():
            return {"path": str(p.resolve()), "saved": True, "sizeBytes": p.stat().st_size}
    except OSError:
        pass
    return {"path": str(p), "saved": False, "sizeBytes": None}


def build_attachment_save_report(
    attachment_candidates: Dict[str, Any],
    saved_attachments: Dict[str, str],
) -> Dict[str, Any]:
    """
    汇总每种附件：接口是否给了 base64、是否落盘成功、本地校验结果。
    """
    report: Dict[str, Any] = {}
    for name, payload in attachment_candidates.items():
        has_b64 = False
        if isinstance(payload, dict) and isinstance(payload.get("base64"), str):
            has_b64 = bool(payload["base64"].strip())
        st = attachment_local_status(saved_attachments.get(name))
        report[name] = {**st, "hadBase64InResponse": has_b64}
    return report


def extract_comment_response_fields(raw: Any) -> Dict[str, Any]:
    """
    Parse ApiReturnInfo<WritingResult> format.
    """
    if not isinstance(raw, dict):
        return {}
    data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
    # 仅使用接口 data.shareUrl，不做启发式补全
    share_url = data.get("shareUrl")
    data_sheet_b64 = _pick_data_sheet_base64(data)
    return {
        "message": raw.get("message"),
        "status": raw.get("status"),
        "code": raw.get("code"),
        "articleId": data.get("articleId"),
        "title": data.get("title"),
        "content": data.get("content"),
        "shareUrl": share_url,
        "wordBase64": data.get("wordBase64"),
        "pdfBase64": data.get("pdfBase64"),
        "dataSheetBase64": data_sheet_b64,
        "refIndexList": data.get("refIndexList"),
        "data": data,
    }


def ensure_log_dir(base_dir: Optional[str] = None, run_id: Optional[str] = None) -> Path:
    if base_dir:
        root = Path(base_dir)
    else:
        root = default_output_root()
    root.mkdir(parents=True, exist_ok=True)
    rid = run_id or datetime.now().strftime("%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:8]
    p = root / rid
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json_log(log_dir: Path, filename: str, data: Any) -> str:
    path = log_dir / filename
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(path)


def save_attachment_payload(
    payload: Dict[str, Any],
    output_dir: str,
    default_name: str,
) -> Optional[str]:
    """
    Save attachment payload to local path.
    Supported inputs:
    - {"base64": "...", "filename": "..."}
    - {"bytes": [1,2,3], "filename": "..."}
    - {"binary": [1,2,3], "filename": "..."}
    Returns saved path or None.
    """
    if not isinstance(payload, dict):
        return None
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    name = str(payload.get("filename") or default_name)
    path = out / name
    if isinstance(payload.get("base64"), str):
        b64 = payload["base64"].strip()
        if not b64:
            return None
        raw = base64.b64decode(b64)
        path.write_bytes(raw)
        return str(path)
    for key in ("bytes", "binary"):
        arr = payload.get(key)
        if isinstance(arr, list):
            try:
                path.write_bytes(bytes(int(x) & 0xFF for x in arr))
                return str(path)
            except Exception:
                return None
    return None

