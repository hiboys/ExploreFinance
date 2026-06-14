# SDD-RIPER Workflow Quick Reference

总纲：`Pre-Research -> RIPER`，全程按 SDD 维护 Spec。

## 启动顺序（按复杂度）

1. `Pre-Research Utilities（非 RIPER 阶段）`
2. `标准流（中大型任务）`：`create_codemap -> build_context_bundle -> sdd_bootstrap（启动 Research）`
3. `快速流（小任务/模糊需求）`：`sdd_bootstrap（启动 Research） -> 按需补 create_codemap/build_context_bundle`
4. `RIPER 正式开始于 RESEARCH`：`Research -> (Innovate, 可选) -> Plan -> Execute -> Review`

## 六个动作的定位

- `create_codemap`：Pre-Research 代码索引动作（`feature` 功能级 / `project` 项目级），用于加速后续对话并节约 token
- `build_context_bundle`：Pre-Research 需求整理动作（目录输入 -> 全模态需求汇总），支持 Lite/Standard 两种输出粒度与 best-effort 解析
- `sdd_bootstrap`：RIPER 启动命令（进入 Research 第一步，完成 Pre-Research 收口并产首版 spec）
- `review_spec`：Plan 后的建议性预审动作，按当前阶段评审并输出 `Spec Review Matrix + Readiness Verdict(GO/NO-GO)`（不阻塞执行）
- `review_execute`：Execute 后质量门禁动作，按三轴输出 `Review Matrix + Overall Verdict + Plan-Execution Diff`
- `archive`：任务闭环后的知识沉淀动作，按 `human/llm` 视角输出复用文档并附 `Trace to Sources`

## sdd_bootstrap 输入容错与提问准则

- 容错输入：只要需求有意义，就可启动。
- 自动补全：优先自己找信息（codemap/context/代码/历史 spec）。
- 提问策略：鼓励多问，但每个问题必须服务于 research 决策。
- 无效提问定义：重复问、与任务无关、为问而问。

## 产物命名规则（统一时间前缀）

- `create_codemap(feature)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<feature>功能.md`
- `create_codemap(project)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project>项目总图.md`
- `build_context_bundle`：`mydocs/context/YYYY-MM-DD_hh-mm_<task>_context_bundle.md`
- `sdd_bootstrap`：`mydocs/specs/YYYY-MM-DD_hh-mm_<TaskName>.md`
- `archive(human)`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_human.md`
- `archive(llm)`：`mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_llm.md`
- 规则：时间前缀不可省略，业务名不可擅改。

## 阶段完成标准（DoD）

- **RESEARCH DoD**：明确需求边界、现状链路、已知风险，并写入 spec。
- **INNOVATE（可选）DoD**：若执行则完成方案对比与取舍；若跳过需写明跳过原因。
- **PLAN DoD**：产出文件改动清单、签名变化、原子 checklist。
- **EXECUTE DoD**：代码改动与 plan 对齐，执行日志回写 spec。
- **REVIEW DoD**：三轴评审完整（Spec质量与达成 / Spec-代码一致性 / 代码自身质量），并给出 `Overall Verdict` 与偏差清单。

## Spec 产物策略

- 首版 Spec 只要求完成 Research 最小章节；Plan/Execute/Review 内容按阶段补齐。
- 任务闭环前再达到完整 Spec（或显式 `Skipped + Reason`）。

## 阶段门禁

- RESEARCH 门禁：优先引用 `Requirement Source + Codemap + Context`；小任务允许最小化输入，但需在 spec 标注信息缺口。
- INNOVATE 门禁：复杂任务默认 2-3 方案；小任务可跳过但需在 spec 标注原因。
- PLAN 门禁：必须包含 `File Changes + Signatures + Checklist`。
- PLAN 后建议：执行 `review_spec`；其 `NO-GO` 为建议项，用户可选择继续执行并记录决策。
- `review_spec` 采用分阶段检查：未到阶段的章节只提醒，不作为阻塞依据。
- EXECUTE 门禁：仅在 `Plan Approved` 后执行。
- REVIEW 门禁：必须输出 `Review Matrix + Overall Verdict + Plan-Execution Diff`；任一高风险阻塞项未解决不得收口。
- ARCHIVE 门禁：默认只归档不删源文件；活跃 spec 归档需显式确认。

## 关键约束

- No Spec, No Code
- Spec is Truth
- Reverse Sync
- Review FAIL -> 回到 Research/Plan

## 多项目协作（自动发现 + 作用域隔离）

### 启动方式

- `sdd_bootstrap: mode=multi_project, task=..., goal=..., requirement=...`
- 无需手动列项目；Agent 自动扫描 workdir 识别子项目（通过 `package.json`/`pom.xml`/`go.mod` 等标志文件）
- 也可显式提供 `projects=[...]` 跳过自动发现
- 智能降级：仅 1 个子项目 → 单项目模式；0 个子项目 → workdir 本身作为单项目

### 多项目 DoD（阶段完成标准）

- **RESEARCH DoD**：Project Registry 已确认，每个子项目有 codemap，跨项目依赖已识别
- **PLAN DoD**：File Changes / Signatures / Checklist 按项目分组；跨项目改动有 Contract Interfaces
- **EXECUTE DoD**：按依赖顺序执行（Provider → Consumer）；Touched Projects 已记录
- **REVIEW DoD**：per-project regression risk + cross-project consistency 检查通过

### 多项目门禁

- 每轮必须声明 `active_project` + `active_workdir`
- 默认 `change_scope=local`，仅改当前项目
- `change_scope=cross` 需显式触发，且必须：加载目标项目 codemap → 检查目标 Spec 冲突 → 记录 Contract Interfaces → 记录 Touched Projects
- 切换项目前必须先加载目标项目 codemap（codemap-first）

### 多项目触发词

- `MULTI / 多项目`：进入多项目模式，运行自动发现
- `CROSS / 跨项目`：当前轮 `change_scope=cross`
- `SWITCH <project_id> / 切换 <project_id>`：切换 active_project，自动加载 codemap
- `REGISTRY / 项目列表`：显示当前 Project Registry
- `SCOPE LOCAL / 回到本地`：重置为 `change_scope=local`

## 常用触发词（汇总）

- `create_codemap: scope=<范围>`（`mode` 可选，默认 `feature`）
- `create_codemap: mode=project, scope=<项目>`
- `build_context_bundle: <目录路径>`
- `sdd_bootstrap: task=..., goal=..., requirement=...`
- `MAP / 链路梳理 / 只看代码`：输出功能级 codemap
- `PROJECT MAP / 全局地图 / 项目总图 / MAP ALL`：输出项目级 codemap
- `FAST / 快速 / >>`：小改极速通道（事后同步 spec）
- `REVIEW SPEC / 评审规格 / 计划评审`：执行 `review_spec`（建议性预审）
- `REVIEW EXECUTE / 代码评审 / 实现复盘`：执行 `review_execute` 三轴审查
- `ARCHIVE / 归档 / 沉淀`：执行 `archive`（汇报版 + 模型版知识沉淀）
- `DEBUG / 排查 / 日志分析`：Debug 排查模式（日志 + Spec + 代码三角定位）
- `验证功能`：Debug 验证模式（全链路日志 vs Spec 逐条比对）
- `MULTI / 多项目`：多项目模式（自动发现 + 作用域隔离）
- `CROSS / 跨项目`：允许跨项目改动
- `SWITCH <id> / 切换 <id>`：切换活跃项目
- `REGISTRY / 项目列表`：查看项目注册表
- `SCOPE LOCAL / 回到本地`：回到本地作用域
