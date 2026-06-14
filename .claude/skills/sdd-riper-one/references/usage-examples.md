# SDD-RIPER 使用示例（贴合实战）

## 1) 一键启动（推荐）

用户输入：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- task=资源访问审批与时效控制
- goal=支持审批授权并做时效管控
- requirement=docs/prd/sample_approval.md
```

预期行为：

- 作为 RIPER 启动命令，收口 Pre-Research 输入并进入 research 第一步。
- 生成首版 spec，并列出待补充上下文与风险。
- 产物文件示例：`mydocs/specs/YYYY-MM-DD_hh-mm_资源访问审批与时效控制.md`。

## 1.1) 口述输入也可直接 bootstrap

用户输入：

```text
这次要做访问控制时效化，先给我跑 sdd_bootstrap。需求比较乱，后面我再补文档。
```

预期行为：

- 直接进入 research，不因输入不规整而阻塞。
- 模型主动补充读取项目代码与历史资料。
- 主动提问关键澄清问题（可多问，但不问废话）。

## 2) create_codemap（随时触发）

用户输入：

```text
create_codemap: mode=feature, scope=访问审批链路, boundary=share 模块, no_code_change=true
```

预期行为：

- 输出入口、核心类、数据流、依赖、风险。
- 作为后续 SDD 的代码索引，减少重复扫描与无效上下文。
- 写入 `mydocs/codemap/` 下的功能级地图文件。
- 产物文件示例：`mydocs/codemap/YYYY-MM-DD_hh-mm_访问审批链路功能.md`。

## 2.1) create_codemap（项目级总图）

用户输入：

```text
create_codemap: mode=project, scope=sample-enterprise, goal=输出项目级总图与核心流程
```

预期行为：

- 输出项目分层、模块边界、跨模块依赖、外部系统依赖、风险热区。
- 建议包含 Mermaid 架构图 + 主流程图；受限时可用结构化文字图替代。
- 产物文件示例：`mydocs/codemap/YYYY-MM-DD_hh-mm_sample-enterprise项目总图.md`。

## 3) build_context_bundle（目录输入）

用户输入：

```text
build_context_bundle: ./mydocs/context/raw/external-share
```

预期行为：

- 阅读目录内多类型文件并汇总（文本/文档/图片）。
- 对图片执行 OCR/视觉提炼；信息不足时允许先索引后迭代补全。
- 产出精炼的需求背景包（需求事实/业务规则/验收口径/约束/冲突点/开放问题）。
- 小需求或信息不完整时可先产出 Lite 版，再迭代补全。
- 产物文件示例：`mydocs/context/YYYY-MM-DD_hh-mm_资源访问审批与时效控制_context_bundle.md`。

## 4) 无 codemap/context 也可继续

用户输入：

```text
先不要做 codemap 和 context bundle，直接 sdd_bootstrap 启动；
缺失项请在 spec 里标注并给我补齐建议。
```

预期行为：

- 不阻塞流程，先产首版 spec。
- 明确缺口与下一步补齐动作。

## 5) Innovate / Plan / Execute / Review 串行

用户输入：

```text
进入 innovate，给 2-3 个方案并对比；我选定后进入 plan；plan approved 后再 execute。
```

预期行为：

- innovate 给多方案+取舍。
- plan 给文件级变更、签名、原子 checklist。
- execute 严格按 plan。
- review 输出三轴结论：Spec质量与达成、Spec-代码一致性、代码自身质量。

补充（小任务）：

- 可跳过 Innovate 直接进 Plan，但要在 spec 中写明跳过原因。

## 6) FAST 小改

用户输入：

```text
>> 只改登录页文案，把“手机号”改为“手机号码”，并同步 spec。
```

预期行为：

- 直接执行小改。
- 改后补齐 spec 记录。

## 7) bootstrap 后完整对话（辅导模板）

用户输入（第一轮）：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- task=审批时效控制
- goal=审批通过后授权自动过期
- requirement=docs/prd/approval_expire.md
```

模型预期输出（摘要）：

- 已生成首版 spec（含 Context Sources / Open Questions）。
- 提出待确认项（例如入口统一性、历史兼容边界、回滚策略）。
- 建议下一步进入 Research 深化。

用户输入（第二轮）：

```text
继续 research，先补齐 create_codemap，范围=审批授权链路。
```

用户输入（第三轮）：

```text
进入 innovate，给 2 个方案，我选后再 plan。
```

用户输入（第四轮）：

```text
方案 B，进入 plan，给出文件改动、签名变化、checklist。
```

用户输入（第五轮）：

```text
Plan Approved，开始 execute。
```

用户输入（第六轮）：

```text
进入 review_execute，对照 spec 做三轴评审并给出总体结论；若失败回到 plan。
```

---

## 8) 多项目协作：自动发现 + 一键启动

### 8.1) 最简启动（自动发现，零配置）

用户输入：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- mode=multi_project
- task=前后端联动发布
- goal=并行推进 web-console 与 api-service 的发布功能
- requirement=docs/prd/release.md
```

预期行为：

- Agent 自动扫描当前 workdir，通过标志文件（`package.json`、`pom.xml` 等）发现子项目。
- 输出 Project Registry 并请用户确认：

  ```
  发现以下子项目：
  | project_id   | project_path    | project_type | marker_file    |
  |-------------|-----------------|-------------|----------------|
  | web-console | ./web-console   | typescript  | package.json   |
  | api-service | ./api-service   | java        | pom.xml        |
  确认是否正确？如需调整请告知。
  ```

- 用户确认后，自动为每个子项目生成 codemap。
- 产出首版多项目 Spec（含 `§0.1 Project Registry`、`§0.2 Multi-Project Config`）。
- 默认 `active_project=web-console`，`change_scope=local`。

### 8.2) 显式指定项目列表（跳过自动发现）

用户输入：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- mode=multi_project
- task=前后端联动发布
- goal=并行推进 web-console 与 api-service
- requirement=docs/prd/release.md
- projects=[{id:web-console,path:./web-console},{id:api-service,path:./api-service}]
```

预期行为：

- 跳过自动发现，直接使用用户提供的项目列表。
- 其余流程与 8.1 一致。

### 8.3) 切换活跃项目

用户输入：

```text
切换 api-service
```

预期行为：

- Agent 更新 `active_project=api-service`，`active_workdir=./api-service`。
- 自动加载 api-service 的 codemap。
- 后续操作仅限 api-service 目录。

### 8.4) 跨项目改动

用户输入：

```text
跨项目：api-service 新增 POST /api/release 接口，web-console 对接该接口。
```

预期行为：

- Agent 设置 `change_scope=cross`。
- 加载两个项目的 codemap。
- 检查两个项目是否有活跃 Spec 冲突。
- Research 阶段识别跨项目依赖关系。
- Plan 阶段：
  - checklist 按项目分组，api-service（Provider）在前，web-console（Consumer）在后。
  - 新增 `§4.4 Contract Interfaces` 记录接口契约。
- Execute 阶段：先改 api-service，再改 web-console。
- Review 阶段：校验接口契约一致性 + 记录 Touched Projects。

### 8.5) 多项目完整对话流（端到端）

用户输入（第一轮）：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- mode=multi_project
- task=用户权限统一管控
- goal=api-service 提供权限接口，web-console 和 admin-portal 对接
- requirement=docs/prd/permission.md
```

模型预期输出（第一轮）：

- 自动发现 3 个子项目（api-service、web-console、admin-portal）。
- 请求用户确认 Project Registry。
- 自动生成 3 个项目的 codemap。
- 产出首版多项目 Spec。

用户输入（第二轮）：

```text
确认项目列表。继续 research，重点分析权限接口的现状。
```

用户输入（第三轮）：

```text
进入 plan，给出按项目分组的改动清单和接口契约。
```

模型预期输出（第三轮）：

- Plan 按项目分组：api-service → web-console → admin-portal。
- Contract Interfaces 表记录 `GET /api/permissions` 接口契约。
- 等待 `Plan Approved`。

用户输入（第四轮）：

```text
Plan Approved，execute all。
```

模型预期输出（第四轮）：

- 按依赖顺序执行：api-service 先 → web-console 次 → admin-portal 最后。
- 每个项目改动后更新 Execute Log。
- 记录 Touched Projects。

用户输入（第五轮）：

```text
进入 review。
```

模型预期输出（第五轮）：

- per-project regression risk 评估。
- cross-project consistency 检查（接口契约匹配）。
- Touched Projects 完整性校验。
- 输出三轴 `Review Matrix` + `Overall Verdict` + `Plan-Execution Diff`。

### 8.6) 智能降级（多项目）

用户输入：

```text
sdd_bootstrap: mode=multi_project, task=修复登录bug, goal=修复登录页报错
```

预期行为（workdir 下仅 1 个子项目）：

- Agent 发现仅 1 个子项目，自动降级为单项目模式。
- 通知用户：`仅发现 1 个子项目 (web-app)，已自动降级为单项目模式。`
- 后续按单项目标准流执行。

---

## 9) Debug 模式：日志驱动排查与功能验证

### 9.1) 排查模式（指定日志 + 问题描述）

用户输入：

```text
DEBUG: log_path=./logs/app-2026-02-27.log, issue=审批通过后目标用户未获得预期授权
```

预期行为：

- Agent 读取日志文件，提取审批回调相关的调用链和异常信息。
- 加载关联的 Spec 和 CodeMap，理解“审批通过 → 自动授权”的预期链路。
- 交叉比对日志证据 × Spec 预期 × 代码逻辑，输出根因分析报告：
  - **症状**：日志中审批回调已触发，但后续授权动作未执行。
  - **预期行为**：审批通过后应触发自动授权。
  - **根因候选**：回调处理链路中的开关条件未命中（灰度或配置未开启）。
  - **建议修复**：检查配置、开关与目标范围是否正确生效。
- 如需修复代码，提示用户进入 RIPER 流程或 FAST 通道。

### 9.2) 验证模式（全链路日志 + Spec 比对）

用户输入：

```text
验证功能: log_path=./logs/release-test/, spec=mydocs/specs/2026-02-27_14-30_资源访问审批与时效控制.md
```

预期行为：

- Agent 读取日志目录下的全链路日志。
- 加载 Spec，逐条提取验收标准（Acceptance Criteria）。
- 输出验证报告（表格形式）：
  - 每条验收标准 → 日志证据 → PASS / FAIL / INCONCLUSIVE。
- 对 INCONCLUSIVE 项给出建议（如"建议增加耗时日志"）。

### 9.3) 简化触发（只给日志路径）

用户输入：

```text
排查 ./logs/error-2026-02-27.log
```

预期行为：

- Agent 读取日志，自动提取错误和异常。
- 结合 CodeMap 索引定位相关代码。
- 输出可能的问题点和建议。

---

## 10) review_spec：执行前规格评审（建议性）

用户输入：

```text
REVIEW SPEC: spec=mydocs/specs/2026-02-27_14-30_资源访问审批与时效控制.md, scope=plan_only
```

预期行为：

- Agent 重读 Spec 的 Requirements + Plan。
- 输出 `Spec Review Matrix` 与 `Readiness Verdict (GO/NO-GO)`。
- 给出 `Risks & Suggestions`，帮助用户决定是否先修 Spec。
- 未到阶段的章节只放入 `Phase Reminders`，不要求当轮补齐全量 spec。
- 若结论 `NO-GO` 但用户坚持执行，允许继续并在 Spec 记录 `User Decision: Proceed despite NO-GO`。

---

## 11) review_execute：执行后三轴评审（推荐）

用户输入：

```text
REVIEW EXECUTE: spec=mydocs/specs/2026-02-27_14-30_资源访问审批与时效控制.md, scope=changed_only
```

预期行为：

- Agent 先重读 Spec（需求/Plan/Execute Log）和已改代码。
- 按三轴输出 `Review Matrix`：
  - Axis-1：Spec 质量与目标/需求达成
  - Axis-2：Spec-代码一致性（文件、签名、checklist、行为）
  - Axis-3：代码自身质量（正确性、鲁棒性、可维护性、测试、风险）
- 产出 `Overall Verdict` 与 `Blocking Issues`。
- 回写 Spec 的 `§6 Review Verdict` 与 `§7 Plan-Execution Diff`。

---

## 12) archive：中间产物归档沉淀（推荐在任务收口执行）

用户输入（双视角）：

```text
ARCHIVE: targets=[mydocs/specs/2026-02-27_14-30_资源访问审批与时效控制.md,mydocs/codemap/2026-02-27_13-50_访问审批链路功能.md], kind=mixed, audience=both, mode=snapshot, topic=访问审批时效化
```

预期行为：

- Agent 读取目标 spec/codemap，并先给出 Source Index。
- 合并重复结论，冲突信息显式标注，不做静默覆盖。
- 生成双文档：
  - `mydocs/archive/YYYY-MM-DD_hh-mm_访问审批时效化_human.md`
  - `mydocs/archive/YYYY-MM-DD_hh-mm_访问审批时效化_llm.md`
- 两个文档都包含 `Trace to Sources`（结论 -> 来源文件/章节）。

用户输入（主题归档）：

```text
主题归档: targets=./mydocs/specs/, kind=spec, audience=llm, mode=thematic, topic=审批域授权策略演进
```

预期行为：

- 从多个 spec 提炼可复用约束、接口契约、代码触点与历史坑位。
- 输出单个 LLM 归档文档，供后续模型任务直接引用。
