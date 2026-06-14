# 原生命令动作详细参数

> 本文件是 `SKILL.md` 中"原生命令动作"段落的完整展开。默认不常驻上下文，仅在需要查看命令详细参数时按需加载。

## 1) `create_codemap`

- 用途：生成代码索引地图，支持 `feature` / `project`（默认 `feature`）
- 本质：CodeMap 是代码上下文索引，用于后续按需加载，而不是每轮全仓扫描。
- 输入：`scope`（建议明确）；`mode` 可选；`goal` 可选
- 输出：
  - `feature`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<feature>功能.md`
  - `project`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project>项目总图.md`
- 要点：
  - `feature` 关注入口、核心链路、依赖、风险
  - `project` 关注架构层、核心模块、跨模块流程、外部依赖；图示建议优先 Mermaid（受限可降级为结构化文字图）

## 2) `build_context_bundle`

- 用途：整理需求上下文，替用户读资料并提炼细节
- 输入：目录路径
- 解析策略：best effort，支持文本/文档/图片；不可解析文件进入 `Unparsed Sources`，不阻塞产出
- 输出：`mydocs/context/YYYY-MM-DD_hh-mm_<task>_context_bundle.md`
- 输出级别：
  - `Lite`：`Source Index`、`Requirement Snapshot`、`Open Questions`、`Next Actions`
  - `Standard`：`Requirement Facts`、`Business Rules`、`Acceptance Criteria`、`Constraints`、`Conflicts & Ambiguities` 等

## 3) `sdd_bootstrap`

- 用途：RIPER 启动命令（进入 Research 第一步，并产出第一版 spec）
- 输入：只要是"有意义且真实的需求"即可（口述/文档/聊天记录/context bundle 均可）
- 执行动作：
  - 汇总用户输入 + 代码事实 + 历史资产（codemap/context/spec）
  - 冲突处理：先落首版 spec 标记冲突，再给 `Option A/B` 和推荐决策
  - 形成首版研究结论与下一步动作
- 输出：`mydocs/specs/YYYY-MM-DD_hh-mm_<TaskName>.md`
- 首版最小内容：`Context Sources`、`Codemap Used`、`Research Findings`、`Open Questions`、`Next Actions`

## 4) `review_spec`

- 用途：在 `Plan` 完成后、`Execute` 前进行 spec 质量评审（建议性，不阻塞执行）
- 输入：
  - `spec`：spec 文件路径（可选，默认当前活跃 spec）
  - `scope`：`plan_only`（默认）或 `full`
- 评审重点：
  1. 目标/范围/验收标准是否清晰且可验证
  2. `Plan` 是否可执行（文件、签名、checklist 是否原子化）
  3. 风险、回滚、跨项目契约（如有）是否充分
- 分阶段原则：
  - 仅评审"当前阶段应当具备"的章节，不要求一次性覆盖全 spec
  - 对尚未到阶段的章节只做 `Reminder`，不计入 `NO-GO`
- 输出：
  - `Spec Review Matrix`（逐项 `PASS/FAIL/PARTIAL` + 证据）
  - `Readiness Verdict`：`GO/NO-GO`（**建议性结论**）
  - `Risks & Suggestions`（若继续执行需关注项）
  - `Phase Reminders`（按阶段待补齐项）
- 约束：
  - `NO-GO` 不构成硬阻塞；若用户坚持执行，允许继续
  - 用户选择继续时，必须在 spec 记录 `User Decision: Proceed despite NO-GO`

## 5) `review_execute`

- 用途：在 `Execute` 后执行结构化评审，输出可回写 spec 的审查结论
- 输入：
  - `spec`：spec 文件路径（可选，默认当前活跃 spec）
  - `scope`：`changed_only`（默认）或 `full`（全量评审）
- 评审三轴（必须全部输出）：
  1. **Spec 质量与目标达成**：spec 是否写清目标、范围、验收标准；需求是否完成
  2. **Spec-代码一致性**：代码是否忠实执行 `Plan`（文件、签名、checklist、行为）
  3. **代码自身质量**：脱离 spec 后，代码在正确性、鲁棒性、可维护性、测试、风险上的质量
- 输出：
  - `Review Matrix`（三轴逐项 `PASS/FAIL/PARTIAL` + 证据）
  - `Overall Verdict`（`PASS/FAIL`）与 `Blocking Issues`
  - `Plan-Execution Diff`（偏差与原因）
- 门禁：
  - 轴 1 或轴 2 任一 `FAIL` -> `Review FAIL`，回到 `Research/Plan`
  - 轴 3 存在高风险问题 -> `Review FAIL`，回到 `Plan`

## 6) `archive`

- 用途：对指定 spec/codemap（或目录）做归档沉淀，将"中间产物"提炼为可复用知识
- 输入：
  - `targets`：文件或目录路径（支持多个）
  - `kind`：`spec` / `codemap` / `mixed`
  - `audience`：`human` / `llm` / `both`（默认 `both`）
  - `mode`：`snapshot`（单任务归档，默认）/ `thematic`（跨任务主题归档）
  - `topic`：归档主题名（可选，默认从 targets 推断）
- 输出：
  - `human`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_human.md`（汇报视角）
  - `llm`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_llm.md`（后续开发参考视角）
  - 每个归档文档必须包含 `Trace to Sources`（结论 -> 来源文件）避免失真
- 门禁：
  - 有活跃执行中的 spec（未完成 Review）时，禁止归档该 spec
  - 默认只归档不删除原文件；删除/移动需用户显式授权
- 自动化脚本（推荐）：
  - `python3 scripts/archive_builder.py --targets mydocs/specs mydocs/codemap --kind mixed --audience both --mode thematic --topic <主题>`
  - 如需强制归档活跃 spec：追加 `--allow-active-spec`（仅在用户明确确认后使用）
