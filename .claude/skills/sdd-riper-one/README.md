# sdd-riper-one

SDD-RIPER ONE Skill（Spec 驱动研发）。

该 Skill 用于约束大模型严格按以下流程执行研发任务：

`Research -> (Innovate, 可选) -> Plan -> (Plan Approved) -> Execute -> Review`

## 工作方式优先

这个仓库更推荐把 `sdd-riper-one` 当成一种**工作方式**来使用，而不是当成一组必须死记硬背的显式命令。

最重要的不是先记住 `create_codemap`、`build_context_bundle`、`sdd_bootstrap` 这些名字，而是先形成下面这套默认习惯：

- `No Spec, No Code`
- `No Approval, No Execute`
- `Spec is Truth`
- 先形成最小 spec / summary / checkpoint，再进入执行
- 复杂任务走完整阶段门禁，小任务也不能裸改

显式命令是能力接口，不是唯一入口。真正该让团队先学会的，是**先收敛任务，再批准执行**。

## TL;DR（30 秒上手）

- 总纲：`Pre-Research -> RIPER`，全程遵循 SDD 并维护 Spec。
- 先记住三句话：`No Spec, No Code`、`No Approval, No Execute`、`Spec is Truth`。
- 不要一开始就要求直接改代码；先让模型形成最小 spec、summary 或 checkpoint。
- 中大型任务默认走完整阶段门禁；小任务也先收敛目标、范围、约束与验证方式。
- 显式命令是补充接口，不是主入口；你给口述需求、文档、聊天记录都可以启动。
- 只要你没明确回复 `Plan Approved`，就不应该进入 `Execute`。

## 使用策略（团队标准）

- **主入口**：`sdd-riper-one` Skill（必装）。
- **Prompt**：可选增强（有则更稳，无也可用）。
- **MCP**：可选提效，不是必需依赖。
- **底线**：`No Spec, No Code` + `Plan Approved` 前不得改代码。

### 推荐的最小启动方式

给 agent 任务时，优先说明：

- `目标`
- `范围`
- `约束`
- `验证方式`

然后要求它：

- 先收敛任务理解
- 先建立最小 spec / summary
- 先给下一步计划与风险
- 等你批准后再进入执行

如果团队先学会的是这套工作方式，而不是某一条具体 prompt，后续无论换模型、换工具还是换执行入口，都更稳定。

## 推荐流程（工作方式视角）

- 标准流（中大型任务）：
  - `create_codemap -> build_context_bundle -> sdd_bootstrap -> Research -> (Innovate, 可选) -> Plan -> Execute -> Review`
- 快速流（小任务/需求模糊）：
  - `sdd_bootstrap -> （按需补）create_codemap/build_context_bundle -> Research -> Plan -> Execute -> Review`
- 关键门禁：
  - 首版 spec 落盘前，不进入后续实现阶段。
  - 未收到精确字样 `Plan Approved`，禁止进入 `Execute`。
  - `Review` 不通过，必须回到 `Research/Plan` 闭环修正。

## Multi-Project Collaboration（自动发现 + 作用域隔离）

**用户零配置**：只需 `mode=multi_project`，Agent 自动完成项目发现、codemap 生成、作用域隔离。

### 核心能力

- **自动发现**：Agent 扫描 workdir，通过标志文件（`package.json`/`pom.xml`/`go.mod`/`Cargo.toml` 等）自动识别子项目，输出 Project Registry 供用户确认。
- **自动 Codemap**：发现项目后自动为每个子项目生成 `create_codemap(project)`。
- **作用域隔离**：默认 `change_scope=local` 只改当前项目；`CROSS / 跨项目` 显式触发跨项目改动。
- **跨项目契约**：跨项目改动自动要求填写 Contract Interfaces（Provider → Consumer → Breaking Change?）。
- **智能降级**：仅 1 个子项目自动降级为单项目模式；0 个子项目则 workdir 本身作为单项目。

### 多项目触发词

| 触发词 | 作用 |
|---|---|
| `MULTI / 多项目` | 进入多项目模式，运行自动发现 |
| `CROSS / 跨项目` | 当前轮允许跨项目改动 |
| `SWITCH <id> / 切换 <id>` | 切换活跃项目，自动加载 codemap |
| `REGISTRY / 项目列表` | 查看当前 Project Registry |
| `SCOPE LOCAL / 回到本地` | 重置为本地作用域 |

## 原生命令动作（Skill 内置）

- `create_codemap`：代码库的**索引与上下文切片**——把庞大代码库压缩为可按需加载的局部上下文，支持功能级 (`feature`) 和项目级 (`project`)；用于后续对话精准定位与节约 token。
- `build_context_bundle`：输入目录路径，读取并提炼需求上下文（支持文本、文档、图片等多类型文件）；支持轻量输出与迭代补全。
- `sdd_bootstrap`：RIPER 启动命令（进入 Research 第一步，同时完成 Pre-Research 收口并产出第一版 spec）。
- `review_spec`：Execute 前的建议性评审命令，按当前阶段检查 spec/plan 并输出 `GO/NO-GO` 建议（不强制阻塞执行）。
- `review_execute`：Execute 后评审命令，按三轴输出 `Review Matrix`（Spec质量与达成 / Spec-代码一致性 / 代码自身质量）并给出 `Overall Verdict`。
- `archive`：归档沉淀命令，对 spec/codemap 做总结、合并、精炼，支持 `human/llm` 双视角输出并附来源追踪。
- `debug`：日志驱动的排查与功能验证——指定日志路径 + 问题描述进行 Bug 三角定位，或指定日志 + Spec 逐条验证功能是否正常。
- 定位：`create_codemap`、`build_context_bundle` 做 Pre-Research 输入准备；`sdd_bootstrap` 负责启动 RIPER；`review_spec` 负责执行前建议性预审；`review_execute` 负责执行后质量门禁；`archive` 负责任务收口后的知识沉淀；`debug` 是独立的旁路模式，需要改代码时自动衔接 RIPER。

## Pre-Research 说明

- 定义：`create_codemap`、`build_context_bundle` 用于进入 RIPER 前的研究准备与信息压缩；`sdd_bootstrap` 作为 RIPER 启动命令，负责收口并进入 Research。
- 标准流（中大型任务）：先 `create_codemap -> build_context_bundle -> sdd_bootstrap`，再进入 `Research`。
- 快速流（小任务/信息不全）：先 `sdd_bootstrap`，在 `Research` 内按需补 `create_codemap` 或 `build_context_bundle`。
- 进入 RIPER 的判断：首版 spec 已落盘，且当前信息缺口已显式标注。

## 推荐顺序（中大型任务）

1. `create_codemap`（先看清代码地图，复杂任务优先 `project` 模式）
2. `build_context_bundle`（把需求文档/图片/记录汇总成可研究上下文）
3. `sdd_bootstrap`（基于 codemap + context 启动首版 spec，并进入 Research）

## 最小启动示例（示意，不是唯一入口）

如果你需要给团队一个最小示例，建议给这种“工作方式模板”，而不是让大家先背整套动作名：

```text
请使用 sdd-riper-one 先收敛任务，不要直接改代码。
先给我：
- 你对任务的理解
- 最小 spec / summary
- 下一步计划
- 风险
- 验证方式
我批准后再执行。
```

如果你需要显式调用内置动作，再使用下面这些命令式示例。

在会话中可直接输入：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- task=资源访问审批与时效控制
- goal=支持审批授权与时效控制
- requirement=docs/prd/sample_approval.md
若已有 codemap/context 可一并引用；没有也先继续并列出待补充项。
```

多项目场景（自动发现，无需手动列项目）：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- mode=multi_project
- task=前后端联动发布
- goal=并行推进 web-console 与 api-service 的发布功能
- requirement=docs/prd/release.md
```

也可显式指定项目列表（跳过自动发现）：

```text
请启用 $sdd-riper-one，并执行 sdd_bootstrap：
- mode=multi_project
- task=前后端联动发布
- goal=并行推进 web-console 与 api-service
- requirement=docs/prd/release.md
- projects=[{id:web-console,path:./web-console},{id:api-service,path:./api-service}]
```

## Bootstrap 后续步骤（辅导版）

1. **Research**：补背景、补约束、补链路，持续修正首版 spec。
2. **Innovate（可选）**：复杂任务输出 2-3 方案并对比；小任务可跳过并记录原因。
3. **Plan**：给文件级改动、签名、原子 checklist，等待你确认。
4. **Review Spec（可选）**：执行 `review_spec` 做执行前建议性预审（分阶段检查）；若 `NO-GO` 你仍可选择继续执行。
5. **Execute**：仅在你明确回复 `Plan Approved` 后改代码。
6. **Review / review_execute**：按三轴输出评审矩阵与总体结论；不通过则回到 Research/Plan。
7. **Archive**：任务收口后归档 spec/codemap，生成可汇报的 human 文档与可复用的 llm 文档。

补充：首版 spec 只需覆盖 Research 最小章节，Plan/Execute/Review 章节按阶段补齐。

## 说明

- README 负责说明默认工作方式与常见启动路径。
- `create_codemap`、`build_context_bundle`、`sdd_bootstrap`、`review_spec`、`review_execute` 等名字，是 skill 提供的能力接口。
- 推荐先让团队掌握“如何工作”，再去记忆“具体叫什么”。

## archive 自动化（脚本）

可直接执行：

```bash
python3 scripts/archive_builder.py \
  --targets mydocs/specs mydocs/codemap \
  --kind mixed \
  --audience both \
  --mode thematic \
  --topic 主题名
```

- 产出：
  - `mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_human.md`
  - `mydocs/archive/YYYY-MM-DD_hh-mm_<topic>_llm.md`
- 默认不会归档活跃 spec；如确需强制，追加 `--allow-active-spec`。

## sdd_bootstrap 输入与提问策略

- 输入不强制格式：口述、文档、聊天记录、bundle 都可直接启动。
- 输入越完整，启动越快；但不完整也可先进入 research。
- 模型应主动补全项目内信息（codemap/context/代码/历史 spec）。
- 提问鼓励“多问且问透”，但必须有价值（不是凑问题）。

## 新手常见误区

- 误区 1：还没 plan 就要求直接改代码。
- 误区 2：改完代码不回写 spec。
- 误区 3：把 codemap/context 当成强制前置（它们是可选增强，不是硬依赖）。

## 可选增强（有 MCP 时）

若已接入 MCP，可调用同名动作进行自动化落盘提效；未接入时，模型按 Skill 规则手工完成同等产物。

## 文件命名规则（统一时间前缀）

三类产物统一使用 `YYYY-MM-DD_hh-mm_` 前缀：

- `create_codemap(feature)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<feature>功能.md`
- `create_codemap(project)`：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project>项目总图.md`
- `build_context_bundle`：`mydocs/context/YYYY-MM-DD_hh-mm_<task>_context_bundle.md`
- `sdd_bootstrap`（spec）：`mydocs/specs/YYYY-MM-DD_hh-mm_<TaskName>.md`

未经用户明确允许，不得省略时间前缀，不得擅自改写业务名。

## 快速安装（本地示例）

在测试项目目录执行：

```bash
your-skill-host install /path/to/sdd-riper-one
```

## 发布前检查

1. `SKILL.md`、`agents/openai.yaml`、`references/*.md` 是否齐全。
2. 安装验证：`your-skill-host install /path/to/sdd-riper-one`。
3. 提交并推送到远端主分支。
