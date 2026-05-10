# 公告搜索技能

## 简介
公告搜索技能是一个金融公告搜索引擎，通过调用同花顺问财的公告搜索接口，帮助用户查询A股、港股、基金、ETF等金融标的的最新公告信息。

## 功能特性
- 支持A股、港股、基金、ETF等金融标的公告查询
- 覆盖定期财务报告、分红派息、回购增持、资产重组等多种公告类型
- 智能查询处理，自动拆解复杂查询
- 友好的命令行接口（CLI）
- 支持批量搜索和数据导出
- 完善的数据处理和错误处理机制

## 快速开始

### 环境要求
- Python 3.7+
- 有效的同花顺问财API Key

### 安装步骤
1. 克隆或下载本技能到本地
2. 安装依赖：
   ```bash
   pip install -r scripts/requirements.txt
   ```
3. 设置环境变量：

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

### 基本使用
```bash
# 使用CLI搜索公告
python scripts/__main__.py "贵州茅台 公告"

# 或者直接运行
announcement-search "上市公司业绩预告"
```

## 使用示例

### 搜索特定公司公告
```bash
announcement-search "贵州茅台最近一个月的公告"
```

### 查询业绩预告
```bash
announcement-search "上市公司业绩预告"
```

### 搜索分红公告
```bash
announcement-search "分红派息公告"
```

### 批量搜索
```bash
announcement-search --input queries.txt --output results.csv
```

## 配置说明

### 环境变量配置
```bash
# 设置API Key
export IWENCAI_API_KEY="your_api_key"

# 可选：设置日志级别
export LOG_LEVEL="INFO"
```

### 配置文件
技能支持JSON配置文件，示例配置见`scripts/config.example.json`。

## 直接API调用（curl示例）

### curl调用示例
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
  -H "X-Claw-Trace-Id: $(python3 -c 'import secrets; print(secrets.token_hex(32))')" \
  -d '{
    "channels": ["announcement"],
    "app_id": "AIME_SKILL",
    "query": "贵州茅台 公告"
  }'
```

### Windows PowerShell curl示例
```powershell
# 在PowerShell中设置环境变量后调用
$traceId = python -c "import secrets; print(secrets.token_hex(32))"
curl.exe -X POST "https://openapi.iwencai.com/v1/comprehensive/search" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $env:IWENCAI_API_KEY" `
  -H "X-Claw-Call-Type: normal" `
  -H "X-Claw-Skill-Id: announcement-search" `
  -H "X-Claw-Skill-Version: 1.0.0" `
  -H "X-Claw-Plugin-Id: none" `
  -H "X-Claw-Plugin-Version: none" `
  -H "X-Claw-Trace-Id: $traceId" `
  -d '{
    "channels": ["announcement"],
    "app_id": "AIME_SKILL",
    "query": "贵州茅台 公告"
  }'
```

## 命令行参数

### 基本参数
- `query`: 搜索关键词（字符串）
- `--input`, `-i`: 输入文件路径（用于批量搜索）
- `--output`, `-o`: 输出文件路径
- `--format`, `-f`: 输出格式（csv, json, txt）
- `--limit`, `-l`: 结果数量限制
- `--verbose`, `-v`: 详细输出模式

### 使用示例
```bash
# 基本搜索，输出到控制台
announcement-search "回购增持"

# 搜索并保存为CSV文件
announcement-search "资产重组" --output results.csv --format csv

# 批量搜索
announcement-search --input queries.txt --output results.json --format json

# 限制结果数量
announcement-search "定期报告" --limit 10
```

## 数据格式

### 输入格式
- 单次搜索：直接提供查询字符串
- 批量搜索：文本文件，每行一个查询

### 输出格式
技能支持多种输出格式：

#### CSV格式
```csv
title,summary,url,publish_date
"某某公司2023年度业绩预告","公司预计2023年度净利润同比增长50%-70%","https://example.com/announcement/12345","2024-01-15 09:30:00"
```

#### JSON格式
```json
[
  {
    "title": "某某公司2023年度业绩预告",
    "summary": "公司预计2023年度净利润同比增长50%-70%",
    "url": "https://example.com/announcement/12345",
    "publish_date": "2024-01-15 09:30:00"
  }
]
```

#### 文本格式
```
标题：某某公司2023年度业绩预告
摘要：公司预计2023年度净利润同比增长50%-70%
链接：https://example.com/announcement/12345
发布时间：2024-01-15 09:30:00
---
```

## 错误处理

技能包含完善的错误处理机制：

### 常见错误
1. **API认证失败**: 检查API Key是否正确设置
2. **网络连接错误**: 检查网络连接
3. **参数错误**: 检查输入参数格式
4. **API限制**: 避免频繁请求

### 错误信息示例
```bash
# API认证失败
错误：API认证失败，请检查IWENCAI_API_KEY环境变量

# 网络错误
错误：网络连接失败，请检查网络连接

# 参数错误
错误：查询参数不能为空
```

## 开发指南

### 项目结构
```
announcement-search/
├── README.md                    # 本文件
├── SKILL.md                     # 技能详细文档
├── references/
│   └── api.md                   # API接口文档
└── scripts/
    ├── __main__.py              # CLI入口点
    ├── config.py                # 配置文件
    ├── config.example.json      # 配置示例文件
    ├── requirements.txt         # Python依赖
    ├── setup.py                 # 安装脚本
    ├── announcement_search.py   # 核心搜索逻辑
    └── utils.py                 # 工具函数
```

### 添加新功能
1. 在`announcement_search.py`中添加新的搜索逻辑
2. 在`__main__.py`中添加对应的命令行参数
3. 更新文档说明

## 许可证

本技能遵循MIT许可证。

## 支持与反馈

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件至维护者

## 更新日志

### v1.0.0
- 初始版本发布
- 支持基本公告搜索功能
- 提供CLI接口
- 支持多种输出格式