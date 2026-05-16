---
name: stock-earnings-review
description: >
  依托东方财富数据库，面向沪深京港美五大市场的上市公司/股票，生成业绩点评类输出（含财报分析、业绩解读）。
  当用户明确提出业绩点评、财报分析、业绩解读需求，或出现「业绩点评」「财报点评」「业绩分析」「季报/半年报/年报点评」「财务分析」「盈利分析」「业绩解读」等表述时，应触发本 Skill。
  用户点名具体公司/股票并希望获得业绩与盈利维度的分析评价时，应触发本 Skill。
  即使用户未明说「业绩点评」，只要意图是对该公司财报或业绩作分析解读，也应触发。
---

# 上市公司业绩点评 (stock-earnings-review)

通过用户问句完成**实体识别 → 报告期匹配 → 业绩点评接口生成**，并在本地保存 PDF/Word 附件（base64 解码保存）。`JSON` 过程日志仅在 `debug` 模式落盘。最终对用户返回标题、接口 `content` 文本整理结果、附件本地路径、溯源说明与分享链接。


## 上层编排协议（支持分步骤调用）

本 skill 采用**分步骤调用**：由大模型按流程依次调用  
1) `scripts/validate_entity.py` 获得实体  
2) `scripts/normalize_report_period.py` 获得报告期候选  
3) 大模型基于用户语义选择 `reportDate`  
4) `scripts/call_review_api.py` 生成点评并保存附件

无论采用哪种方式，**禁止**仅由大模型凭知识库「编造」业绩点评全文并冒充 skill 结果。

## 输出目录与文件结构（默认）

与 `mx_macro_data` 相同约定：**默认根目录**为当前工作目录下的 `miaoxiang/stock-earnings-review/`（无需手动创建，脚本会自动 `mkdir`）。

每次执行会在该根目录下再创建**一次运行子目录**（`run_id`，含时间戳与短 UUID），结构如下：

| 路径（相对本次 run 根目录） | 说明 |
|----------------------------|------|
| `01_entity.json` | 实体识别结果（仅 `--debug`） |
| `02_report_period.json` | 报告期列表与匹配结果（仅 `--debug`） |
| `03_comment_raw.json` | 业绩点评接口原始响应（仅 `--debug`） |
| `04_review_result.json` | 解析后的点评结果与章节信息（仅 `--debug`） |
| `05_final_result.json` | 汇总与 `finalOutput`（仅 `--debug`） |
| `attachments/review.pdf` | 接口返回 `pdfBase64` 解码后的文件（若接口有返回） |
| `attachments/review.doc` | 接口返回 `wordBase64` 解码后的文件（若接口有返回） |

**说明**：若接口未返回对应 base64，则不会生成对应文件。非 `debug` 模式不会生成 `01~05.json`，但附件仍会保存。

## 环境变量

| 变量名 | 说明 | 默认 |
|--------|------|------|
| `STOCK_EARNINGS_REVIEW_OUTPUT_DIR` | 日志与附件的**根目录**（其下仍按每次 run 分子目录） | `miaoxiang/stock-earnings-review`（相对当前工作目录） |
| `EARNINGS_REVIEW_LOG_DIR` | 与上一项同义，兼容旧配置 | 同上 |



## 快速开始

### 分步骤调用（适配外层大模型编排）

```bash
# 第一步：实体识别
python3 {baseDir}/stock-earnings-review/scripts/validate_entity.py --query "东方财富 业绩点评"

# 第二步：获取报告期候选
python3 {baseDir}/stock-earnings-review/scripts/normalize_report_period.py \
  --secu-code 300059 --market-char SZ --class-code 002001

# 第三步：外层大模型选择 reportDate 后调用点评
python3 {baseDir}/stock-earnings-review/scripts/call_review_api.py \
  --secu-code 300059 --market-char SZ --class-code 002001 \
  --report-date 2025-12-31 --secu-name 东方财富
```

可选参数：

| 参数 | 说明 | 必填 |
|------|------|------|
| `validate_entity.py --query` | 用户原始问句（需含公司/股票信息） | ✅ |
| `normalize_report_period.py --selected-report-date` | 可选，由上层模型已决策时传入；传入值须在候选列表中 | 否 |
| `call_review_api.py --attachment-dir` | 附件保存目录；不传则默认为 `miaoxiang/stock-earnings-review/<run_id>/attachments` | 否 |
| `call_review_api.py --debug` | 输出完整中间字段并落盘调试日志 | 否 |

注意：**禁止调用 任何「后台执行、稍后汇报」的方式跑本脚本**，只能在当前会话中同步等待到命令完成，拿到 stdout 的结果后再继续，否则会导致本 Skill 失败。

---

## 处理流程（摘要）

整体流程分为三步：实体识别与市场校验 → 报告期匹配 → 生成点评并落盘。

### 第一步：实体识别与市场校验

调用 `scripts/validate_entity.py`，将用户**原始问句**传入实体识别接口，返回 `secuCode`、`marketChar`、`classCode`、`secuName` 等；多个实体时取第一个。

### 第二步：报告期匹配

调用 `scripts/normalize_report_period.py` 获取报告期列表；由**上层模型**根据用户意图选择 `reportDate`（或通过 `--report-date` 传入）。若用户未指定报告期，默认取列表中**最新一期**（以脚本实现为准）。

`/assistant/write/choice/reportList` 接口返回的是该实体**已发布**的报告期列表，不包含未发布报告期。
例如请求 `{"emCode":"NVDA.O"}` 时，返回结果即为英伟达已发布报告期集合。

### 第三步：业绩点评与落盘

调用 `scripts/call_review_api.py`，请求业绩点评接口，解析标题与正文 `content`，将 PDF/Word base64 写入 `attachments/`。各阶段 JSON 日志仅在 `debug` 模式写入。

#### 对用户输出格式（逻辑）

- **标题**：接口返回标题。
- **正文**：直接基于接口返回的 `content` 文本进行整理后输出。
- **分享链接**：接口返回的 `shareUrl`。
- **文件路径**：返回 `files.pdf` / `files.word` / `files.dataSheet`（若生成）。

第三步 `call_review_api.py` 输出仅使用以下字段：`title`、`content`、`shareUrl`、`files`。

#### 输出格式模板（Markdown 示意）

```markdown
# {title}

{content}

如需查看详细信息，请查看附件 PDF 或 DOC.......
- **附件**：{files}
- **分享链接**：{shareUrl}
```

### 关键约束（必须遵守）

- 不要尝试读取、解析或总结 `review.pdf` / `review.doc` 的文件内容。
- 不要因为 PDF 文本截断或 DOC 为二进制而再次走“读附件内容”的流程。
- 仅基于 `call_review_api.py` 返回的结构化字段（尤其是 `summary`/`content`）整理并回复用户。

### 前置校验失败约束（必须遵守）

- 出现以下任一情况必须立即停止流程，不得继续调用后续接口，不得编造结果：
  - 实体识别为空或实体不在支持范围；
  - 报告期列表为空；
  - 用户指定的 `selected_report_date` 不在候选列表（`strict` 模式）。
- 当脚本返回 `ok=false` 或返回体中存在 `message` 字段时，必须原样输出 `message`，不得改写或替换。
- 当报告期匹配失败且运行在非严格模式时，可回退到最新一期，但必须明确提示“已回退到最新可用报告期”。

---

## 格式要求

响应中的数学公式格式：

- 行内公式使用 `\(...\)` 格式（不使用 `$...$`）
- 行间公式使用 `\[...\]` 格式
- 行间公式块内部内容保持不变

## 错误处理汇总

| 错误场景 | 处理方式 |
|----------|----------|
| 问句中无实体 | 向用户确认需要点评的公司名称 |
| 实体识别失败 | 提示用户确认公司名称或股票代码 |
| 实体不在支持市场 | 返回「目前仅支持沪深京港美实体进行业绩点评」 |
| 报告期列表为空 | 提示「暂无该实体的可用报告期数据」 |
| 报告期接口调用失败 | 提示「暂时无法获取报告期信息，请稍后重试」 |
| 业绩点评接口调用失败 | 提示「业绩点评生成失败，请稍后重试」 |
| 用户要求看完整正文 | 直接返回接口 `content` 文本；如需原文件可提示附件路径，但不读取附件内容 |

## 脚本与文档

| 脚本/文件 | 功能 |
|-----------|------|
| `scripts/validate_entity.py` | 实体识别 |
| `scripts/normalize_report_period.py` | 报告期列表与匹配 |
| `scripts/call_review_api.py` | 业绩点评接口与附件落盘 |
| `BUSINESS_LOGIC.md` | **业务逻辑详版**：前置检查、报告期 A 股/港美股规则、交付模板、完整错误表、与脚本 `strict` 模式说明 |

编排层实现完整规则时请同时阅读 `BUSINESS_LOGIC.md`。
