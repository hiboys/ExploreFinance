# 多项目协作详细规则

> 本文件是 `SKILL.md` 中"多项目协作"段落的完整展开。默认不常驻上下文，仅在触发 `MULTI / 多项目` 时按需加载。

## 自动发现（Auto-Discovery）

- 触发：`sdd_bootstrap: mode=multi_project` 或触发词 `MULTI / 多项目`
- Agent 自动扫描 `workdir` 下子目录，通过标志文件识别子项目：
  - JS/TS: `package.json` | Java/Kotlin: `pom.xml`, `build.gradle` | Go: `go.mod` | Python: `pyproject.toml`, `setup.py` | Rust: `Cargo.toml` | 通用: `.git`
  - Monorepo: 额外检查 `workspaces`、`settings.gradle`、`pnpm-workspace.yaml`
- 产出 `Project Registry`（`§0.1`），报告给用户确认后继续
- 用户也可显式提供 `projects=[...]` 跳过自动发现
- 智能降级：仅 1 个子项目 → 自动降级为单项目模式；0 个子项目 → workdir 本身作为单项目

## 自动 Codemap

- 发现项目后，自动为每个子项目检查/生成 `create_codemap(project)`
- 产物路径：`mydocs/codemap/YYYY-MM-DD_hh-mm_<project_id>项目总图.md`

## 作用域隔离规则（必须）

- 每轮先声明 `active_project` 与 `active_workdir`
- 默认 `change_scope=local`，只允许修改 `active_project` 下的文件
- 仅在显式 `change_scope=cross`（或触发词 `CROSS / 跨项目`）时允许跨项目改动
- 始终 `codemap-first`：切换到任何项目前，必须先加载该项目的 codemap/context
- 跨项目执行后，在 spec `§6.1 Touched Projects` 记录改动项目、文件、原因

## 跨项目依赖与契约

- 跨项目改动时，必须在 spec `§4.4 Contract Interfaces` 记录：Provider → Interface → Consumer → 是否 Breaking Change → 迁移方案
- 跨项目 Plan 的 checklist 按项目分组，Provider 优先于 Consumer 执行
- 修改前检查目标项目是否有活跃 Spec，有冲突则 STOP 等待用户决策

## 多项目 Review（扩展）

- 校验跨项目契约一致性（Provider 与 Consumer 接口匹配）
- 校验 Touched Projects 完整性
- 校验无孤立改动（所有改动文件都在已注册项目内）
- 按项目分别评估回归风险

## 触发词

- `MULTI / 多项目` → 进入多项目模式，运行自动发现
- `CROSS / 跨项目` → 当前轮 `change_scope=cross`
- `SWITCH <project_id> / 切换 <project_id>` → 切换 `active_project`，自动加载 codemap
- `REGISTRY / 项目列表` → 显示当前 Project Registry
- `SCOPE LOCAL / 回到本地` → 重置为 `change_scope=local`

## 最小启动示例

```text
sdd_bootstrap: mode=multi_project, task=<任务名>, goal=<目标>, requirement=<需求文档或描述>
```

- 无需手动列项目，Agent 自动发现并确认。
- 也可显式指定：`projects=[{id:web-console,path:./web-console},{id:api-service,path:./api-service}]`
