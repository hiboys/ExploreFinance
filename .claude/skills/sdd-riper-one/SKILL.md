---
name: sdd-riper-one
description: 将 SDD-RIPER 方法论落地为严格可执行流程的技能。用于代码/架构任务中的“功能级与项目级 CodeMap 生成、全模态需求上下文打包、Spec 驱动研发、RIPER 阶段门禁推进”，适用于 Claude/Codex/其他 CLI Agent 的多轮协作开发。
---

# SDD-RIPER-ONE Skill

## 全局行为与安全底线 (Global Safeguards)

- **高危操作阻断**：永远不要静默或提议执行 `git clean`（包含任何参数，特别是 `-fdx`），防止用户未提交的工作区数据不可逆丢失。
- **研发纪律**：
  - `No Spec, No Code`：未形成并持久化 Spec 前，不进入代码实现。
  - `No Approval, No Execute`：未得到执行许可前，禁止进行环境修改或高风险变更。
  - `Spec is Truth`：任何聊天决议或最新改动必须回源到 Spec，Spec 是唯一真相源。

## 核心定位

- 先读一次：`references/sdd-riper-one-protocol.md`
- 总纲：`Pre-Research -> RIPER`，全程遵循 SDD 并持续维护 Spec
- 三条底线：`No Spec, No Code`、`Spec is Truth`、`Reverse Sync`
- `create_codemap` / `build_context_bundle` 是 Pre-Research 输入准备；`sdd_bootstrap` 是 RIPER 启动命令（进入 Research 第一步，同时完成 Pre-Research 收口）
- RIPER 主流程：`Research -> (Innovate, 可选) -> Plan -> Execute -> Review`
- 不要在每轮对话里重载整份 Skill / Spec；默认只回读当前阶段需要的小节
- **Spec 受众分层与上下文保护**：Spec 的第一受众是人类（持久化的任务上下文与组织记忆），第二受众才是模型。协议对模型的核心价值是四件事：**注意力聚焦**（让模型在当前阶段只关注该关注的）、**信息索引**（需要时按路径回读，而非全量常驻）、**防止上下文腐烂**（用落盘的 Spec 对抗长对话中的遗忘与漂移）、**辅助 Review**（提供 Spec vs 代码的交叉验证基准）。协议绝不应导致上下文被塞满挤爆——RIPER 管流程，Spec 管记录，模型按需取用。

## 推荐流程（直接执行）

- 标准流（中大型任务）：
  - `create_codemap -> build_context_bundle -> sdd_bootstrap -> Research -> (Innovate, 可选) -> Plan -> Execute -> Review`
- 快速流（小任务/需求模糊）：
  - `sdd_bootstrap -> （按需补）create_codemap/build_context_bundle -> Research -> Plan -> Execute -> Review`
- 门禁：
  - 首版 spec 落盘前，不进入实现
  - 未收到精确字样 `Plan Approved`，禁止进入 `Execute`
  - `Review` 不通过，回到 `Research/Plan` 修正

## 上下文装配规则

- `SDD` 是完整持久化上下文与记忆层：必须完整落盘、持续维护，但不要求每轮整份常驻输入
- `RIPER` 是审批驱动状态机：必须在每轮保持当前 `phase`、当前批准状态与下一步动作清晰可见
- 裁剪目标是减少重复重放，不是减少约束或弱化门禁

### 热上下文（每轮必带）

- 当前 `phase`
- 当前 `approval status`
- 当前 `spec path`
- 当前 `Goal`
- 当前 `In Scope / Out of Scope`
- 当前活跃 `Checklist`
- 当前 `Open Questions`
- 当前风险与 `Next Action`
- 热上下文只用于当前轮聚焦，不替代完整 spec；与 spec 冲突时，永远以 spec 为准

### 温上下文（切阶段或高风险动作前加载）

- `Research -> Plan`：`Research Findings`、关键事实、方案结论
- `Plan -> Execute`：`File Changes`、`Signatures`、原子 `Checklist`
- `Execute -> Review`：`Validation`、实际改动摘要、偏差说明
- 执行 `review_spec` / `review_execute` 时，回读对应评审区块

### 冷上下文（默认不带，命中再加载）

- 全量 `Change Log`
- 历史 `Research` 细节
- 完整 `codemap`
- 完整 `context bundle`
- `MULTI` / `DEBUG` / `ARCHIVE` 的完整扩展规则
- 长示例、长模板、长 quick reference

### 硬门禁（不可因裁剪而削弱）

- 没有 spec，不进入代码实现
- `phase` 与 `approval status` 必须是显式状态，不允许根据语气、倾向或不完整表述推断
- 没有精确字样 `Plan Approved`，不进入 `Execute`
- phase 切换前，必须回读对应 spec 区块；不能只靠热上下文跨阶段推进
- `Review` 时必须基于 plan 与 validation，而不是只看聊天摘要
- 发现冲突、字段缺失、摘要过期或记忆不确定时，立即回读完整 spec 或相关原文区块

### 回读触发规则

- **每轮必带**：`phase`、`approval status`、`spec path`、`Goal`、当前活跃 `Checklist`、`Next Action`
- **切阶段时**：回读目标阶段对应的 spec 区块（Research Findings / File Changes / Validation 等）
- **执行 review 时**：`review_spec` 回读 Plan 区块，`review_execute` 回读 Plan + Validation + Review 区块
- **触发全量回读**：阶段切换有争议、摘要与 spec 冲突、长对话出现遗忘迹象、高风险改动
- **禁止**：不能用热上下文替代 spec 原文跨阶段推进，不能根据模糊语气推断 `Plan Approved`

## 多项目协作（自动发现 + 作用域隔离）

- 目标：多项目场景下保持"局部理解 + 局部执行 + 显式边界"，**用户零额外配置**。
- 详细协议：`references/sdd-riper-one-protocol.md` → `MULTI-PROJECT PROTOCOL` 段
- Spec 模板：`references/spec-template.md` → 多项目模板

### 自动发现（Auto-Discovery）

- 触发：`sdd_bootstrap: mode=multi_project` 或触发词 `MULTI / 多项目`
- Agent 自动扫描 `workdir` 下子目录，通过标志文件识别子项目：
  - JS/TS: `package.json` | Java/Kotlin: `pom.xml`, `build.gradle` | Go: `go.mod` | Python: `pyproject.toml`, `setup.py` | Rust: `Cargo.toml` | 通用: `.git`
  - Monorepo: 额外检查 `workspaces`、`settings.gradle`、`pnpm-workspace.yaml`
- 产出 `Project Registry`（`§0.1`），报告给用户确认后继续
- 用户也可显式提供 `projects=[...]` 跳过自动发现
- 智能降级：仅 1 个子项目 → 自动降级为单项目模式；0 个子项目 → workdir 本身作为单项目

### 自动 Codemap

- 发现项目后，自动为每个子项目检查/生成 `create_codemap(project)`
- 产物路径：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project_id>项目总图.md`

### 作用域隔离规则（必须）

- 每轮先声明 `active_project` 与 `active_workdir`
- 默认 `change_scope=local`，只允许修改 `active_project` 下的文件
- 仅在显式 `change_scope=cross`（或触发词 `CROSS / 跨项目`）时允许跨项目改动
- 始终 `codemap-first`：切换到任何项目前，必须先加载该项目的 codemap/context
- 跨项目执行后，在 spec `§6.1 Touched Projects` 记录改动项目、文件、原因

### 跨项目依赖与契约

- 跨项目改动时，必须在 spec `§4.4 Contract Interfaces` 记录：Provider → Interface → Consumer → 是否 Breaking Change → 迁移方案
- 跨项目 Plan 的 checklist 按项目分组，Provider 优先于 Consumer 执行
- 修改前检查目标项目是否有活跃 Spec，有冲突则 STOP 等待用户决策

### 多项目 Review（扩展）

- 校验跨项目契约一致性（Provider 与 Consumer 接口匹配）
- 校验 Touched Projects 完整性
- 校验无孤立改动（所有改动文件都在已注册项目内）
- 按项目分别评估回归风险

### 触发词

- `MULTI / 多项目` → 进入多项目模式，运行自动发现
- `CROSS / 跨项目` → 当前轮 `change_scope=cross`
- `SWITCH <project_id> / 切换 <project_id>` → 切换 `active_project`，自动加载 codemap
- `REGISTRY / 项目列表` → 显示当前 Project Registry
- `SCOPE LOCAL / 回到本地` → 重置为 `change_scope=local`

### 最小启动示例

```text
sdd_bootstrap: mode=multi_project, task=<任务名>, goal=<目标>, requirement=<需求文档或描述>
```

- 无需手动列项目，Agent 自动发现并确认。
- 也可显式指定：`projects=[{id:web-console,path:./web-console},{id:api-service,path:./api-service}]`

## 原生命令动作（可直接输入）

### 1) `create_codemap`

- 用途：生成代码索引地图，支持 `feature` / `project`（默认 `feature`）
- 本质：CodeMap 是代码上下文索引，用于后续按需加载，而不是每轮全仓扫描。
- 输入：`scope`（建议明确）；`mode` 可选；`goal` 可选
- 输出：
  - `feature`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<feature>功能.md`
  - `project`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project>项目总图.md`
- 要点：
  - `feature` 关注入口、核心链路、依赖、风险
  - `project` 关注架构层、核心模块、跨模块流程、外部依赖；图示建议优先 Mermaid（受限可降级为结构化文字图）

### 2) `build_context_bundle`

- 用途：整理需求上下文，替用户读资料并提炼细节
- 输入：目录路径
- 解析策略：best effort，支持文本/文档/图片；不可解析文件进入 `Unparsed Sources`，不阻塞产出
- 输出：`mydocs/context/YYYY-MM-DD_hh-mm_<task>_context_bundle.md`
- 输出级别：
  - `Lite`：`Source Index`、`Requirement Snapshot`、`Open Questions`、`Next Actions`
  - `Standard`：`Requirement Facts`、`Business Rules`、`Acceptance Criteria`、`Constraints`、`Conflicts & Ambiguities` 等

### 3) `sdd_bootstrap`

- 用途：RIPER 启动命令（进入 Research 第一步，并产出第一版 spec）
- 输入：只要是“有意义且真实的需求”即可（口述/文档/聊天记录/context bundle 均可）
- 执行动作：
  - 汇总用户输入 + 代码事实 + 历史资产（codemap/context/spec）
  - 冲突处理：先落首版 spec 标记冲突，再给 `Option A/B` 和推荐决策
  - 形成首版研究结论与下一步动作
- 输出：`mydocs/specs/YYYY-MM-DD_hh-mm_<TaskName>.md`
- 首版最小内容：`Context Sources`、`Codemap Used`、`Research Findings`、`Open Questions`、`Next Actions`

### 4) `review_spec`

- 用途：在 `Plan` 完成后、`Execute` 前进行 spec 质量评审（建议性，不阻塞执行）
- 输入：
  - `spec`：spec 文件路径（可选，默认当前活跃 spec）
  - `scope`：`plan_only`（默认）或 `full`
- 评审重点：
  1. 目标/范围/验收标准是否清晰且可验证
  2. `Plan` 是否可执行（文件、签名、checklist 是否原子化）
  3. 风险、回滚、跨项目契约（如有）是否充分
- 分阶段原则：
  - 仅评审“当前阶段应当具备”的章节，不要求一次性覆盖全 spec
  - 对尚未到阶段的章节只做 `Reminder`，不计入 `NO-GO`
- 输出：
  - `Spec Review Matrix`（逐项 `PASS/FAIL/PARTIAL` + 证据）
  - `Readiness Verdict`：`GO/NO-GO`（**建议性结论**）
  - `Risks & Suggestions`（若继续执行需关注项）
  - `Phase Reminders`（按阶段待补齐项）
- 约束：
  - `NO-GO` 不构成硬阻塞；若用户坚持执行，允许继续
  - 用户选择继续时，必须在 spec 记录 `User Decision: Proceed despite NO-GO`

### 5) `review_execute`

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

### 6) `archive`

- 用途：对指定 spec/codemap（或目录）做归档沉淀，将“中间产物”提炼为可复用知识
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

## 阶段约束（最小集合）

- 每轮先同步 spec 再推进阶段
- 默认不在每轮对话中重载整份 spec；优先回读当前阶段区块、活跃 checklist、`Open Questions`、最近一次 `Change Log / Validation`
- 仅在切换阶段、执行 `review_spec/review_execute`、发现冲突或明显遗忘时，全量回读 spec
- `codemap` / `context bundle` 按需读取，不作为每轮固定输入
- `Innovate` 可选：复杂任务建议 2-3 方案；小任务可跳过但要写原因
- `Plan` 必须可执行：文件路径 + 签名 + 原子 checklist
- `Plan` 后建议执行 `review_spec`；其 `NO-GO` 为建议项，不是强制门禁
- `Review` 必须按三轴评审并回写结论：`Review Matrix`、`Overall Verdict`、`Plan-Execution Diff`
- 任务闭环后建议执行 `archive`，沉淀 human/llm 双视角知识

## Debug 模式（日志驱动排查与功能验证）

- 用途：基于日志 + Spec + 代码三角定位 Bug，或用全链路日志验证功能是否正常
- 触发词：`DEBUG / 排查 / 日志分析 / 验证功能`
- 输入：
  - `log_path`：日志文件或日志目录路径（必须）
  - `issue`：发现的问题描述 / 报错信息（可选，排查模式时建议提供）
  - `spec`：关联的 Spec 文件路径（可选，验证模式时建议提供）
- 两种子模式：
  - **排查模式**（默认）：用户提供日志 + 问题描述，Agent 结合 Spec 和代码定位可能的 Bug 根因
  - **验证模式**：用户提供全链路日志 + Spec，Agent 逐条比对 Spec 中的预期行为与日志中的实际行为，确认功能是否正常
- 工作流：
  1. 读取日志文件/目录，提取关键错误、异常、调用链信息
  2. 加载关联的 Spec 和 CodeMap（如有），建立"预期行为 vs 实际行为"的对照
  3. 定位代码中的可疑逻辑（结合 CodeMap 索引精准跳转）
  4. 输出结论：Bug 根因分析 / 功能验证报告
  5. 如需修复，自动进入 RIPER 流程（Research → Plan → Execute → Review）
- 约束：
  - Debug 模式本身不直接改代码，只做分析和定位
  - 需要改代码时，必须走 RIPER 流程（或 FAST 通道处理小修复）
  - 分析结论回写到 Spec 的 `§ Debug Log` 段（如有活跃 Spec）

## 触发词

- `MAP / Code Map / 链路梳理 / 只看代码` -> `create_codemap(feature)`
- `PROJECT MAP / 全局地图 / 项目总图 / MAP ALL` -> `create_codemap(project)`
- `MULTI / 多项目` -> 多项目轻量模式（父目录 workdir + 局部执行）
- `CROSS / 跨项目` -> 允许跨项目改动（强制记录 `Touched Projects`）
- `FAST / 快速 / >>` -> 小改快速通道（改后同步 spec）
- `REVIEW SPEC / 评审规格 / 计划评审` -> 执行 `review_spec`（建议性预审）
- `REVIEW EXECUTE / 代码评审 / 实现复盘` -> 执行 `review_execute`（三轴审查）
- `ARCHIVE / 归档 / 沉淀` -> 执行 `archive`（总结、合并、精炼）
- `DEBUG / 排查 / 日志分析 / 验证功能` -> Debug 模式（日志驱动排查与功能验证）
- `EXIT SDD / 退出协议` -> 退出状态机

## 命名规则（统一时间前缀）

- 时间前缀：`YYYY-MM-DD_hh-mm_`
- `create_codemap(feature)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<feature>功能.md`
- `create_codemap(project)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project>项目总图.md`
- `build_context_bundle`：`mydocs/context/YYYY-MM-DD_hh-mm_<task>_context_bundle.md`
- `sdd_bootstrap`：`mydocs/specs/YYYY-MM-DD_hh-mm_<TaskName>.md`
- `archive(human)`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_human.md`
- `archive(llm)`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_llm.md`

## 参考

- `references/sdd-riper-one-protocol.md`
- `references/spec-template.md`
- `references/workflow-quickref.md`
- `references/usage-examples.md`
- `references/archive-template.md`
- `references/multi-project.md`（多项目协作详细规则）
- `references/commands.md`（原生命令动作详细参数）
