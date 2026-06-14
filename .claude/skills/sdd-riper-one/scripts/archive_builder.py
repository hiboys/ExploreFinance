#!/usr/bin/env python3
"""
Build archive documents from spec/codemap markdown files.

Outputs:
- human archive: report-friendly summary
- llm archive: machine-friendly reusable context
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
from dataclasses import dataclass
from typing import List, Sequence, Tuple


@dataclass
class Candidate:
    text: str
    section: str
    source: pathlib.Path


@dataclass
class SourceDoc:
    path: pathlib.Path
    title: str
    sections: List[Tuple[str, List[str]]]
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Archive spec/codemap files into human/llm summary docs."
    )
    parser.add_argument(
        "--targets",
        nargs="+",
        required=True,
        help="Target files/directories (supports multiple values).",
    )
    parser.add_argument(
        "--kind",
        choices=["spec", "codemap", "mixed"],
        default="mixed",
        help="Filter kind for discovered markdown files.",
    )
    parser.add_argument(
        "--audience",
        choices=["human", "llm", "both"],
        default="both",
        help="Which archive docs to generate.",
    )
    parser.add_argument(
        "--mode",
        choices=["snapshot", "thematic"],
        default="snapshot",
        help="Archive mode.",
    )
    parser.add_argument(
        "--topic",
        default="",
        help="Archive topic. If omitted, inferred from targets.",
    )
    parser.add_argument(
        "--output-dir",
        default="mydocs/archive",
        help="Output directory for generated archive docs.",
    )
    parser.add_argument(
        "--allow-active-spec",
        action="store_true",
        help="Allow archiving specs that look active/non-finalized.",
    )
    return parser.parse_args()


def split_target_values(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    for value in values:
        parts = [item.strip() for item in value.split(",")]
        out.extend(item for item in parts if item)
    return out


def is_markdown(path: pathlib.Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".md"


def is_spec_like(path: pathlib.Path) -> bool:
    p = str(path).lower()
    name = path.name.lower()
    return ("/specs/" in p) or ("\\specs\\" in p) or ("spec" in name)


def is_codemap_like(path: pathlib.Path) -> bool:
    p = str(path).lower()
    name = path.name.lower()
    return (
        "/codemap/" in p
        or "\\codemap\\" in p
        or "codemap" in name
        or ("项目总图" in path.name)
        or ("功能" in path.name)
    )


def matches_kind(path: pathlib.Path, kind: str) -> bool:
    if kind == "mixed":
        return True
    if kind == "spec":
        return is_spec_like(path) and not is_codemap_like(path)
    if kind == "codemap":
        return is_codemap_like(path)
    return False


def collect_target_files(targets: Sequence[str], kind: str) -> List[pathlib.Path]:
    files: List[pathlib.Path] = []
    seen = set()

    for raw in targets:
        target = pathlib.Path(raw).expanduser()
        if not target.exists():
            print(f"[WARN] target does not exist: {target}", file=sys.stderr)
            continue

        if target.is_file():
            if is_markdown(target):
                key = str(target.resolve())
                if key not in seen:
                    files.append(target)
                    seen.add(key)
            else:
                print(f"[WARN] skipped non-markdown file: {target}", file=sys.stderr)
            continue

        for path in target.rglob("*.md"):
            if not path.is_file():
                continue
            if not matches_kind(path, kind):
                continue
            key = str(path.resolve())
            if key in seen:
                continue
            files.append(path)
            seen.add(key)

    files.sort(key=lambda p: str(p))
    return files


def extract_sections(text: str) -> List[Tuple[str, List[str]]]:
    sections: List[Tuple[str, List[str]]] = []
    current_title = "Document"
    current_lines: List[str] = []

    heading_pattern = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
    for line in text.splitlines():
        match = heading_pattern.match(line)
        if match:
            sections.append((current_title, current_lines))
            current_title = match.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line.rstrip())

    sections.append((current_title, current_lines))
    return sections


def detect_title(path: pathlib.Path, sections: Sequence[Tuple[str, List[str]]]) -> str:
    for section, _ in sections:
        if section and section != "Document":
            return section
    return path.stem


def load_docs(paths: Sequence[pathlib.Path]) -> List[SourceDoc]:
    docs: List[SourceDoc] = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="ignore")
        sections = extract_sections(text)
        title = detect_title(path, sections)
        docs.append(SourceDoc(path=path, title=title, sections=sections, text=text))
    return docs


def looks_active_spec(doc: SourceDoc) -> bool:
    if not is_spec_like(doc.path):
        return False
    if "Review Verdict" not in doc.text and "## 6. Review Verdict" not in doc.text:
        return True
    if "Overall Verdict: PASS/FAIL" in doc.text:
        return True
    if "Spec coverage: PASS/FAIL" in doc.text or "Behavior check: PASS/FAIL" in doc.text:
        return True
    if re.search(r"Overall Verdict:\s*(PASS|FAIL)\b", doc.text):
        return False
    return True


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[-*+]\s+", "", line)
    line = re.sub(r"^\d+\.\s+", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line


def is_meaningful_line(line: str) -> bool:
    if not line:
        return False
    if line.startswith("```") or line.startswith("|---"):
        return False
    if line.startswith("|") and line.endswith("|"):
        return False
    if len(line) < 8:
        return False
    return True


def collect_candidates(docs: Sequence[SourceDoc]) -> List[Candidate]:
    items: List[Candidate] = []
    for doc in docs:
        for section, lines in doc.sections:
            for raw in lines:
                line = normalize_line(raw)
                if not is_meaningful_line(line):
                    continue
                items.append(Candidate(text=line, section=section, source=doc.path))
    return dedupe_candidates(items)


def dedupe_candidates(candidates: Sequence[Candidate]) -> List[Candidate]:
    out: List[Candidate] = []
    seen = set()
    for item in candidates:
        key = re.sub(r"\s+", " ", item.text).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def pick_by_keywords(
    candidates: Sequence[Candidate], keywords: Sequence[str], limit: int
) -> List[Candidate]:
    selected: List[Candidate] = []
    lowered = [kw.lower() for kw in keywords]
    for item in candidates:
        line = item.text.lower()
        if any(kw in line for kw in lowered):
            selected.append(item)
            if len(selected) >= limit:
                break
    return selected


def fallback_take(candidates: Sequence[Candidate], limit: int) -> List[Candidate]:
    return list(candidates[:limit])


def summarize_items(items: Sequence[Candidate], limit: int = 6) -> List[Candidate]:
    return list(items[:limit])


def infer_topic(raw_topic: str, files: Sequence[pathlib.Path], mode: str) -> str:
    if raw_topic.strip():
        return raw_topic.strip()
    if len(files) == 1:
        name = files[0].stem
        name = re.sub(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}_?", "", name)
        return name or "archive"
    if mode == "thematic":
        return "thematic-archive"
    return "snapshot-archive"


def sanitize_topic(topic: str) -> str:
    topic = topic.strip().replace(" ", "-")
    topic = re.sub(r"[\\/:*?\"<>|]+", "_", topic)
    topic = re.sub(r"_+", "_", topic).strip("._-")
    return topic or "archive"


def rel_or_abs(path: pathlib.Path) -> str:
    try:
        return str(path.resolve().relative_to(pathlib.Path.cwd().resolve()))
    except Exception:
        return str(path.resolve())


def to_markdown_bullets(items: Sequence[Candidate], empty_text: str) -> str:
    if not items:
        return f"- {empty_text}"
    lines = [f"- {item.text}" for item in items]
    return "\n".join(lines)


def to_trace_table(items: Sequence[Candidate], max_rows: int = 18) -> str:
    rows = ["| Conclusion | Source File | Section |", "|---|---|---|"]
    for item in items[:max_rows]:
        conclusion = item.text.replace("|", "\\|")
        source = rel_or_abs(item.source).replace("|", "\\|")
        section = item.section.replace("|", "\\|")
        rows.append(f"| {conclusion} | `{source}` | `{section}` |")
    if len(rows) == 2:
        rows.append("| N/A | N/A | N/A |")
    return "\n".join(rows)


def build_human_archive(
    docs: Sequence[SourceDoc], candidates: Sequence[Candidate], topic: str, mode: str
) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    source_lines = "\n".join(f"- `{rel_or_abs(doc.path)}`" for doc in docs)

    decision = pick_by_keywords(
        candidates,
        ["decision", "selected", "结论", "决策", "方案", "取舍", "why"],
        limit=8,
    )
    outcome = pick_by_keywords(
        candidates,
        ["goal", "完成", "result", "outcome", "验收", "pass", "上线", "收益"],
        limit=8,
    )
    risks = pick_by_keywords(
        candidates,
        ["risk", "风险", "follow-up", "todo", "block", "issue", "regression", "回归"],
        limit=8,
    )

    if not decision:
        decision = fallback_take(candidates, 6)
    if not outcome:
        outcome = fallback_take(candidates[6:], 6) if len(candidates) > 6 else fallback_take(candidates, 6)
    if not risks:
        risks = fallback_take(candidates[12:], 6) if len(candidates) > 12 else fallback_take(candidates, 6)

    trace_items = dedupe_candidates(list(decision) + list(outcome) + list(risks))

    return f"""# Archive (Human): {topic}

## 1. Executive Summary
- Generated At: `{now}`
- Archive Mode: `{mode}`
- Source Count: `{len(docs)}`
- Scope Summary: 基于指定中间产物完成归档沉淀，输出可汇报版本。

## 2. Scope & Sources
{source_lines if source_lines else "- N/A"}

## 3. Key Decisions
{to_markdown_bullets(summarize_items(decision), "No clear decision lines found.")}

## 4. Outcomes & Business Impact
{to_markdown_bullets(summarize_items(outcome), "No explicit outcome lines found.")}

## 5. Risks & Follow-ups
{to_markdown_bullets(summarize_items(risks), "No explicit risk/follow-up lines found.")}

## 6. Trace to Sources
{to_trace_table(trace_items)}
"""


def build_llm_archive(
    docs: Sequence[SourceDoc], candidates: Sequence[Candidate], topic: str, mode: str
) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    source_lines = "\n".join(f"- `{rel_or_abs(doc.path)}`" for doc in docs)

    constraints = pick_by_keywords(
        candidates,
        ["constraint", "must", "禁止", "约束", "门禁", "No Spec", "Plan Approved", "scope"],
        limit=10,
    )
    interfaces = pick_by_keywords(
        candidates,
        ["api", "interface", "contract", "schema", "provider", "consumer", "endpoint"],
        limit=10,
    )
    touchpoints = pick_by_keywords(
        candidates,
        ["entry", "module", "file", "path", "core", "链路", "入口", "依赖"],
        limit=10,
    )
    patterns = pick_by_keywords(
        candidates,
        ["option", "selected", "pattern", "anti-pattern", "recommended", "建议", "避免"],
        limit=10,
    )

    if not constraints:
        constraints = fallback_take(candidates, 8)
    if not interfaces:
        interfaces = fallback_take(candidates[8:], 8) if len(candidates) > 8 else fallback_take(candidates, 8)
    if not touchpoints:
        touchpoints = fallback_take(candidates[16:], 8) if len(candidates) > 16 else fallback_take(candidates, 8)
    if not patterns:
        patterns = fallback_take(candidates[24:], 8) if len(candidates) > 24 else fallback_take(candidates, 8)

    trace_items = dedupe_candidates(
        list(constraints) + list(interfaces) + list(touchpoints) + list(patterns)
    )

    return f"""# Archive (LLM): {topic}

## 1. Task Snapshot
- Generated At: `{now}`
- Archive Mode: `{mode}`
- Source Count: `{len(docs)}`

## 2. Stable Facts & Constraints
{to_markdown_bullets(summarize_items(constraints, 8), "No explicit constraints found.")}

## 3. Interfaces & Contracts
{to_markdown_bullets(summarize_items(interfaces, 8), "No explicit interface/contract lines found.")}

## 4. Code Touchpoints
{to_markdown_bullets(summarize_items(touchpoints, 8), "No explicit code touchpoints found.")}

## 5. Accepted Patterns / Rejected Paths
{to_markdown_bullets(summarize_items(patterns, 8), "No explicit pattern lines found.")}

## 6. Reuse Hints for Future Tasks
- 优先加载本归档中的约束与契约，再读取对应活跃 Spec。
- 若归档结论与活跃 Spec 冲突，以活跃 Spec 为准并记录差异。
- 复用前先检查 `Trace to Sources` 对应来源是否仍然有效。

## 7. Source Index
{source_lines if source_lines else "- N/A"}

## 8. Trace to Sources
{to_trace_table(trace_items)}
"""


def write_file(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    target_values = split_target_values(args.targets)
    if not target_values:
        print("[ERROR] no valid targets provided", file=sys.stderr)
        return 2

    files = collect_target_files(target_values, args.kind)
    if not files:
        print("[ERROR] no markdown files found under targets", file=sys.stderr)
        return 2

    docs = load_docs(files)
    if not args.allow_active_spec:
        active_specs = [doc for doc in docs if looks_active_spec(doc)]
        if active_specs:
            print("[ERROR] active/non-finalized specs detected:", file=sys.stderr)
            for doc in active_specs:
                print(f"  - {doc.path}", file=sys.stderr)
            print(
                "Use --allow-active-spec to override after explicit confirmation.",
                file=sys.stderr,
            )
            return 3

    topic = infer_topic(args.topic, files, args.mode)
    topic_slug = sanitize_topic(topic)
    timestamp = dt.datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_dir = pathlib.Path(args.output_dir)

    candidates = collect_candidates(docs)

    generated: List[pathlib.Path] = []
    if args.audience in ("human", "both"):
        human_text = build_human_archive(docs, candidates, topic, args.mode)
        human_path = out_dir / f"{timestamp}_{topic_slug}_human.md"
        write_file(human_path, human_text)
        generated.append(human_path)

    if args.audience in ("llm", "both"):
        llm_text = build_llm_archive(docs, candidates, topic, args.mode)
        llm_path = out_dir / f"{timestamp}_{topic_slug}_llm.md"
        write_file(llm_path, llm_text)
        generated.append(llm_path)

    print("[OK] archive generated:")
    for path in generated:
        print(f"  - {path}")
    print(f"[INFO] source files: {len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
