# Archive Template (Human + LLM)

本模板用于 `archive` 指令输出，支持 `human` 与 `llm` 两个视角。可按 `snapshot`（单任务）或 `thematic`（跨任务）使用。

---

## Human Archive Template

```markdown
# Archive (Human): <Topic>

## 1. Executive Summary
- 背景与目标: ...
- 本次归档范围: ...
- 结论摘要: ...

## 2. Scope & Sources
- Archive Mode: `snapshot` / `thematic`
- Source Targets:
  - `mydocs/specs/...`
  - `mydocs/codemap/...`
- Time Window: ...

## 3. Key Decisions
- 决策 1: ...
- 决策 2: ...

## 4. Outcomes & Business Impact
- 已完成能力: ...
- 验收结果: ...
- 业务影响/收益: ...

## 5. Risks & Follow-ups
- 已知风险: ...
- 后续建议: ...

## 6. Trace to Sources
| Conclusion | Source File | Section / Evidence |
|---|---|---|
| ... | `mydocs/specs/...` | `§4 Plan` |
| ... | `mydocs/codemap/...` | `核心链路` |
```

---

## LLM Archive Template

```markdown
# Archive (LLM): <Topic>

## 1. Task Snapshot
- Goal: ...
- In-Scope: ...
- Out-of-Scope: ...

## 2. Stable Facts & Constraints
- 事实约束 1: ...
- 事实约束 2: ...

## 3. Interfaces & Contracts
- API / Schema / Event:
  - Provider: ...
  - Consumer: ...
  - Breaking Change: Yes/No
  - Notes: ...

## 4. Code Touchpoints
- Entry Points: ...
- Core Files/Modules: ...
- Hotspots & Risks: ...

## 5. Accepted Patterns / Rejected Paths
- Accepted:
  - ...
- Rejected:
  - ...

## 6. Reuse Hints for Future Tasks
- 推荐复用步骤: ...
- 常见坑位与规避: ...

## 7. Trace to Sources
| Statement | Source File | Section / Evidence |
|---|---|---|
| ... | `mydocs/specs/...` | `§6 Review Verdict` |
| ... | `mydocs/codemap/...` | `架构图` |
```
