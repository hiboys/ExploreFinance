---
name: industry-stock-tracker
description: >
  依托东方财富数据库，面向行业或个股，产出跟踪类报告（含日报/周报/月报、研报及结构化跟踪解读）。
  满足以下任一条件即触发：（1）用户明确索要「报告」「研报」「跟踪分析」或定期跟踪类文稿；（2）用户点名的行业、板块、指数、个股（名称或代码），并期望系统化、可成文的近况跟踪或梳理。
  典型说法如「写一份 XX 行业报告」「跟踪 XX 股票」「生成 XX 日报」「看看 XX 最近怎么样并出报告」等。

---

# 行业/个股跟踪报告生成 Skill

## 概述

本 skill 用于将用户自然语言问题交给脚本 `scripts/generate_industry_stock_tracker_report.py`，
由脚本调用远程报告服务并返回统一 JSON 结果。输出包含标题、总结内容与附件本地保存路径（DOCX/PDF）。


## 核心工作流

1) 将用户原始问题原样作为 `query` 传入脚本。  
2) 脚本调用接口生成报告并获取“总结”章节。  
3) 若接口返回 `wordBase64/pdfBase64`，脚本会落地为本地附件文件并返回路径。  
4) 将脚本标准输出（JSON）直接作为 skill 输出依据，不做与脚本冲突的二次改写。

命令行参数调用方式：

```
python3 {baseDir}/scripts/generate_industry_stock_tracker_report.py --query "{{query}}"
```

注意：**禁止调用 任何「后台执行、稍后汇报」的方式跑本脚本**，只能在当前会话中同步等待到命令完成，拿到 stdout 的结果后再继续，否则会导致本 Skill 失败。

## 输出格式规范

接口返回后，必须严格按以下模板输出，不得增删标题、不得改变顺序、不得添加额外章节：

### 标题
直接使用接口返回的 `title` 字段，单独成行。

### 正文
如果接口返回的 `content` 字段有相关行业报告信息，则原文透传；
否则读取接口返回的附件文件内容，总结相关报告信息返回，记住保证返回的正文内容非空。

### 附件
接口返回 pdf 以及 docx 格式文件的保存路径。

### 分享链接
直接使用接口返回的 `share_url` 字段，单独成行。文案必须按以下固定格式输出：

```
{标题}

{正文}

完整报告：
- PDF：{pdf_path}
- DOCX：{docx_path}

分享链接：
{share_url}
```

字段映射规则：
- `{title}` = 脚本返回的 `title`
- `{content}` = 脚本返回的 `content`
- `{pdf_path}` = `attachments` 中 `type=PDF` 对应的 `url`
- `{docx_path}` = `attachments` 中 `type=DOCX` 对应的 `url`
- `{share_url}` = 脚本返回的 `share_url`

当附件缺失时：
- 若仅有一种格式，仅输出存在的那一行（PDF 或 DOCX）。
- 若两种都不存在，输出：`完整报告：暂无可用附件`

## 语言要求

始终优先中文输出。若用户使用其他语言，可在交互提示中适度双语，但报告正文与字段含义保持中文语境。

## 使用约束与建议

- 不要在 skill 层重写脚本已生成的 `content` 主体结构，避免与脚本逻辑漂移。  
- 除附件路径展示外，不在 skill 层追加二次总结，正文以脚本 `content` 结果为准。  
- 若脚本返回 `ok=false`，优先透传 `message`；不要自行编造错误原因。  
- 该 skill 目标是“生成并返回结果”，不是在 skill 内追加长篇二次分析。

## 常见错误处理：
- 缺少 query：`BAD_REQUEST`，message 为“缺少 query 参数”。  
- 不支持实体：`ERROR_ENTITY`，message 为“目前暂不支持此类实体体进行分析。”  
- 网络/超时/服务异常：`TIMEOUT` / `NETWORK_ERROR` / `HTTP_ERROR` / `UNEXPECTED_ERROR`，对用户统一提示“报告生成服务暂时不可用，请稍后重试。”。

错误输出强约束：
- 只要接口响应或脚本标准输出（print 的 JSON）中存在 `message` 字段，模型必须输出该 `message`，不得省略、不得改写、不得替换为其他话术。
- 当 `ok=false` 时，优先输出错误 `message`；若同时存在 `error_code`，可附带展示 `error_code`，但不影响 `message` 原样透传。
