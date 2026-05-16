---
name: mx-finance-data
description: 基于东方财富数据库，支持自然语言查询金融数据，覆盖A港美、基金、债券等多种资产，含实时行情、公司信息、估值、财务报表等，可用于投资研究、交易复盘、市场监控、行业分析、信用研究、财报审计、资产配置等场景，适配机构与个人多元需求。返回结果包含数据说明及 xlsx 文件。Natural language query for financial data across all markets, including A-shares, ETFs, bonds, Hong Kong and US stocks, and funds. It provides L1/L2 data, financial indicators, company profiles and valuation metrics. Ideal for investment research, strategy backtesting, market monitoring and industry analysis. It meets the needs of diverse institutions and individuals.
---

# 金融数据查询

## 功能范围

### 1. 支持查询的对象范围
* 股票（A 股、港股、美股）
* 板块、指数、股东
* 企业发行人、债券、非上市公司
* 股票市场、基金市场、债券市场

### 2. 支持查询的数据类型

支持查询以下类型的结构化数据：

* **实时行情**（现价、涨跌幅、盘口数据等）
* **量化数据**（技术指标、资金流向等）
* **报表数据**（营收、净利润、财务比率等）

### 3. 支持的查询方式与**严格限制**

支持多实体、多指标、多时间范围的组合查询。**受后端接口限制，单次查询必须遵循以下配额：**

* **实体上限**：单次最多支持 **5 个** 股票/金融实体。
* **处理逻辑**：若用户请求超过上述限制，Skill 将优先处理前 5 个实体，并在结果说明文件中予以提示。

> **示例：** “查询 A、B、C、D、E、F 六只股票的营收” -> 仅返回前五只。

### 4. 输出结果

Skill 执行后会输出以下文件：

- 一个查数结果 `xlsx` 文件，用于承载结构化查询结果
- 一个结果说明 `txt` 文件，用于描述查询内容、结果含义及必要说明

------

## 查询示例

### 基础指标查询

- 东方财富的基本面
- 贵州茅台最近一年的营业收入和净利润
- 半导体etf的业绩表现

### 实时行情与盘口查询

- 当前300059的实时买单
- 英伟达现在的最新价和涨跌幅
- 沪深300当前点位和成交额

### 多实体、多指标、多时间查询（注意配额）

* **合规示例**：对比创业板指、沪深300、中证500（3个实体）春节以来的涨幅（1个指标）。
* **合规示例**：东方财富、拼多多（2个实体）最近一年的营收、毛利、净利（3个指标）。
* **超限提示**：若查询“沪深前十大权重股的PE”，系统将截取前 5 名进行查询。

------

## 补充说明

- 本 Skill 面向金融结构化数据与关系数据查询，不侧重主观分析、投资建议或资讯解读。
- 语句中必须包含明确的金融实体名称。
- 当用户使用自然语言发起查询时，Skill 可根据问句内容识别查询对象、指标和时间范围，并输出结构化结果文件。
- 对于支持范围内的查询请求，优先输出结构化查数结果，并同时生成结果说明文件，便于后续使用。


### 3. 安装依赖


```bash
pip3 install httpx pandas openpyxl --user
```

## 快速开始

### 在工作目录下执行

```bash
python3 {baseDir}/scripts/get_data.py --query "贵州茅台近期走势如何"
```

### 输出示例

```
xlsx: /path/to/miaoxiang/mx_finance_data/mx_finance_data_9535fe18.xlsx
描述: /path/to/miaoxiang/mx_finance_data/mx_finance_data_9535fe18_description.txt
行数: 42
```

### 输出文件说明

| 文件 | 说明 |
| --- | --- |
| `mx_finance_data_<查询id>.xlsx` | 结构化数据表，包含请求的实体与指标 |
| `mx_finance_data_<查询id>_description.txt` | 包含查询逻辑说明、字段含义及**配额截断提示** |


