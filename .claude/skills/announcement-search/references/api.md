# 问财公告搜索 API 文档

## 概述
问财公告搜索 API 提供公告信息的搜索功能，通过用户问句查询相关公告信息。

## 基础信息
- **Base URL**: `https://openapi.iwencai.com`
- **接口路径**: `/v1/comprehensive/search`
- **请求方式**: POST
- **Content-Type**: `application/json`

## 认证
API 使用 API Key 进行认证，需要在请求头中设置：
- **Header**: `Authorization: Bearer {IWENCAI_API_KEY}`
- **环境变量**: `IWENCAI_API_KEY` (用户侧申请的 API Key)

## 请求参数

### 请求头 (Headers)
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Content-Type | string | 是 | 必须设置为 `application/json` |
| Authorization | string | 是 | Bearer token 认证，格式: `Bearer {IWENCAI_API_KEY}` |

### 请求体 (Body)
请求体为 JSON 格式，包含以下参数：

#### 固定参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| channels | array | 是 | 搜索渠道类型 | `["announcement"]` |
| app_id | string | 是 | 应用 ID | `"AIME_SKILL"` |

#### 可变参数
| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| query | string | 是 | 用户问句，搜索关键词 | `"上市公司业绩预告"` |

### 请求示例
```json
{
  "channels": ["announcement"],
  "app_id": "AIME_SKILL",
  "query": "上市公司业绩预告"
}
```

## 响应

### 响应格式
响应为 JSON 格式，包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| data | array | 返回的文章信息列表 |

### data 字段结构
`data` 数组中的每个元素包含以下字段：

| 字段名 | 类型 | 说明 | 格式 |
|--------|------|------|------|
| title | string | 文章标题 | - |
| summary | string | 文章摘要 | - |
| url | string | 文章网址 | URL 格式 |
| publish_date | string | 文章发布时间 | `YYYY-MM-DD HH:MM:SS` |

### 响应示例
```json
{
  "data": [
    {
      "title": "某某公司2023年度业绩预告",
      "summary": "公司预计2023年度净利润同比增长50%-70%",
      "url": "https://example.com/announcement/12345",
      "publish_date": "2024-01-15 09:30:00"
    },
    {
      "title": "另一家公司重大合同公告",
      "summary": "公司与客户签订重大销售合同，金额约10亿元",
      "url": "https://example.com/announcement/12346",
      "publish_date": "2024-01-14 16:45:00"
    }
  ]
}
```

## 错误处理

### HTTP 状态码
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败 |
| 500 | 服务器内部错误 |

### 错误响应示例
```json
{
  "error": {
    "code": "AUTH_FAILED",
    "message": "API Key 无效或已过期"
  }
}
```

## 使用示例

### Python 示例
```python
import requests
import os

# 从环境变量获取 API Key
api_key = os.getenv("IWENCAI_API_KEY")

# 请求头
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# 请求体
payload = {
    "channels": ["announcement"],
    "app_id": "AIME_SKILL",
    "query": "上市公司业绩预告"
}

# 发送请求
response = requests.post(
    "https://openapi.iwencai.com/v1/comprehensive/search",
    headers=headers,
    json=payload
)

# 处理响应
if response.status_code == 200:
    data = response.json()
    for article in data["data"]:
        print(f"标题: {article['title']}")
        print(f"摘要: {article['summary']}")
        print(f"发布时间: {article['publish_date']}")
        print(f"链接: {article['url']}")
        print("---")
else:
    print(f"请求失败: {response.status_code}")
    print(response.text)
```

### cURL 示例
```bash
curl -X POST \
  https://openapi.iwencai.com/v1/comprehensive/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $IWENCAI_API_KEY" \
  -d '{
    "channels": ["announcement"],
    "app_id": "AIME_SKILL",
    "query": "上市公司业绩预告"
  }'
```

## 注意事项
1. **API Key 安全**: 请妥善保管 API Key，不要将其暴露在客户端代码中
2. **请求频率**: 请遵守 API 使用限制，避免频繁请求
3. **参数格式**: `channels` 参数必须为数组格式，且包含 `"announcement"`
4. **时间格式**: `publish_date` 字段使用 24 小时制时间格式
5. **错误处理**: 建议实现完善的错误处理机制

## 数据来源声明
所有公告数据来源于同花顺问财，在使用数据时请注明数据来源。

## 更新日志
- **v1.0.0** (初始版本): 基础公告搜索功能

## 支持
如有问题或需要技术支持，请联系 API 提供商。