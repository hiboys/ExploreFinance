---
name: announcement-search
description: 支持A股、港股、基金、ETF等金融标的公告的查询，同时公告类型包括不限于定期财务报告、分红派息、回购增持、资产重组等等。
---

# 公告搜索技能

## 版本
当前技能版本：1.0.0

## 技能概述

本技能是一个金融公告搜索引擎，通过调用同花顺问财的公告搜索接口，帮助用户查询A股、港股、基金、ETF等金融标的的最新公告信息。支持查询的公告类型包括但不限于：定期财务报告、分红派息、回购增持、资产重组、重大合同、业绩预告等。

## API Key 获取与配置（首次使用必读）

> 首次使用 - 获取 API Key  
> 所有技能都需要 IWENCAI_API_KEY 环境变量才能使用。 如果用户尚未配置，按以下步骤引导：  
>  
> 步骤 1：获取 API Key  
> 在浏览器内打同花顺i问财SkillHub页面：https://www.iwencai.com/skillhub  
>  
> 步骤 2：登录  
>  
> 步骤 3：点击具体的Skill，打开弹窗查看详情，在安装方式-Agent用户-找到您的IWENCAI_API_KEY这一段，复制  
>  
> 步骤 4：配置环境变量  
> 获取到 API Key 后，直接复制指引文字发送给AI助手，或手动设置环境变量：

### 跨平台环境变量设置

**macOS / Linux (bash/zsh):**
```bash
export IWENCAI_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**
```powershell
$env:IWENCAI_API_KEY="your_api_key_here"
```

**Windows (CMD):**
```cmd
set IWENCAI_API_KEY=your_api_key_here
```

## 技能功能

### 1. 金融公告搜索
- 搜索各类金融公告信息
- 支持A股、港股、基金、ETF等金融标的
- 覆盖定期财务报告、分红派息、回购增持、资产重组等多种公告类型
- 支持中文关键词搜索

### 2. 智能查询处理
- 自动分析用户查询意图
- 根据需求决定是否拆解复杂查询为多个简单查询
- 示例：用户问"最近贵州茅台和五粮液有什么公告？"可以拆分为"贵州茅台 公告"和"五粮液 公告"两个查询
- 根据查询复杂度决定调用接口的次数

### 3. 数据评估与扩展
- 自动评估搜索结果是否能回答用户问题
- 如有必要，可调用其他技能或工具扩展数据
- 对搜索结果进行质量评估和相关性排序

### 4. 数据处理与返回
- 对搜索结果进行排序、过滤和摘要处理
- 生成结构化的数据结果
- 将处理后的数据返回给大模型，帮助回答用户问题

### 5. CLI支持
- 提供友好的命令行接口
- 支持基本搜索、批量搜索、数据导出等功能
- 详细的命令行文档和使用示例

## 使用场景

### 何时调用本技能
1. 当用户需要搜索上市公司最新公告时
2. 当用户查询特定金融标的的公告信息时
3. 当用户需要了解分红派息、回购增持等公告时
4. 当用户查询定期财务报告（年报、季报）时
5. 当用户需要获取资产重组、重大合同等公告信息时

### 使用示例
- "搜索贵州茅台最近一个月的公告"
- "查询宁德时代的业绩预告"
- "查看中国平安的分红公告"
- "搜索最近有哪些公司发布了回购计划"
- "查询创业板公司的年报公告"

## 技术实现

### API接口规范（遵循iwencai-skill-creator要求）

#### 基础接口信息
- **Base URL**: `https://openapi.iwencai.com`
- **接口路径**: `/v1/comprehensive/search`
- **请求方式**: POST（优先使用POST，符合规范要求）
- **认证方式**: API Key (Bearer Token)，从环境变量 `IWENCAI_API_KEY` 读取

#### 必需请求头（Claw Headers）
所有发往问财OpenAPI网关的请求必须包含以下Header：

| Header | 取值说明 | 本技能取值 |
|--------|----------|------------|
| `X-Claw-Call-Type` | `normal`：正常请求；`retry`：失败后的重试 | `normal` |
| `X-Claw-Skill-Id` | 技能标识 | `announcement-search` |
| `X-Claw-Skill-Version` | 当前技能版本号 | `1.0.0`（与技能版本一致） |
| `X-Claw-Plugin-Id` | 插件ID（扩展字段） | `none` |
| `X-Claw-Plugin-Version` | 插件版本（扩展字段） | `none` |
| `X-Claw-Trace-Id` | **每次请求新生成**的64字符唯一追踪ID | 使用 `secrets.token_hex(32)` 生成 |

#### 请求参数
- **固定参数**: `channels: ["announcement"]`, `app_id: "AIME_SKILL"`
- **可变参数**: `query` (用户问句)

### 响应格式
API返回的`data`字段包含以下信息：
- `title`: 文章标题
- `summary`: 文章摘要
- `url`: 文章网址
- `publish_date`: 文章发布时间 (格式: YYYY-MM-DD HH:MM:SS)

### curl示例（脱敏）

**Unix/Linux/macOS (bash/zsh):**
```bash
# 使用环境变量中的API Key
curl -X POST "https://openapi.iwencai.com/v1/comprehensive/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $IWENCAI_API_KEY" \
  -H "X-Claw-Call-Type: normal" \
  -H "X-Claw-Skill-Id: announcement-search" \
  -H "X-Claw-Skill-Version: 1.0.0" \
  -H "X-Claw-Plugin-Id: none" \
  -H "X-Claw-Plugin-Version: none" \
  -H "X-Claw-Trace-Id: $(python3 -c 'import secrets; print(secrets.token_hex(32))' 2>/dev/null || openssl rand -hex 32)" \
  -d '{
    "channels": ["announcement"],
    "app_id": "AIME_SKILL",
    "query": "贵州茅台 公告"
  }'
```

**Windows (PowerShell):**
```powershell
# 首先设置环境变量（如果尚未设置）
$env:IWENCAI_API_KEY="your_api_key_here"

# 生成64字符Trace ID
$traceId = -join ((48..57) + (97..102) | Get-Random -Count 64 | % { [char]$_ })

# 发送请求
$headers = @{
    "Content-Type" = "application/json"
    "Authorization" = "Bearer $env:IWENCAI_API_KEY"
    "X-Claw-Call-Type" = "normal"
    "X-Claw-Skill-Id" = "announcement-search"
    "X-Claw-Skill-Version" = "1.0.0"
    "X-Claw-Plugin-Id" = "none"
    "X-Claw-Plugin-Version" = "none"
    "X-Claw-Trace-Id" = $traceId
}

$body = @{
    channels = @("announcement")
    app_id = "AIME_SKILL"
    query = "贵州茅台 公告"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://openapi.iwencai.com/v1/comprehensive/search" -Method Post -Headers $headers -Body $body
```

**通用说明：**
- Trace ID必须是64字符十六进制字符串，每次请求新生成
- API Key必须从环境变量 `IWENCAI_API_KEY` 读取，禁止硬编码
- 所有Claw headers必须正确设置

### 数据来源声明
在模型回答过程中，如果引用了同花顺数据，必须强调数据来源于同花顺问财。

## 安装与使用

### 快速开始
1. 按照前面的"API Key 获取与配置"章节设置环境变量
2. 使用技能搜索公告：`announcement-search "贵州茅台 公告"`

### 配置文件（可选）
技能支持通过配置文件管理API Key等敏感信息，配置文件示例见`scripts/config.example.json`。

### CLI使用示例
```bash
# 基本搜索
announcement-search "上市公司业绩预告"

# 批量搜索（从文件读取查询）
announcement-search --input queries.txt --output results.csv

# 指定输出格式
announcement-search "分红派息" --format json
```

## 注意事项

1. **API Key安全**: 请妥善保管API Key，不要将其暴露在客户端代码中
2. **请求频率**: 请遵守API使用限制，避免频繁请求
3. **数据准确性**: 公告信息来源于同花顺问财，请注意数据时效性
4. **错误处理**: 技能包含完善的错误处理机制，会提示用户相关错误信息

## 支持与反馈

如有问题或需要技术支持，请联系技能维护者。技能会持续更新以提供更好的公告搜索体验。