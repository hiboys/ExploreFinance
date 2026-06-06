---
name: westock-data
description: 查询A股、港股、美股个股/指数/ETF的详细数据，包括：K线/分时、财务报表（三大报表多期查询，支持跨市场批量对比）、资金流向、技术指标、筹码分析、股东结构、分红除权、业绩预告、公司简况、ETF基金数据（详情/持仓/净值）；以及大盘指数、行业/板块行情、板块成份股、板块区间涨幅排行、指数成份股、热搜、新股日历、投资日历等市场数据。
---

# WeStock Data

**数据源**：腾讯自选股行情数据接口 | **支持市场**：A股（沪深/科创/北交所）、港股、美股

---

## 快速开始

> **安全声明**：以下命令使用 `npx -y` 拉取  腾讯自选股团队发布的预编译单文件包（零运行时依赖），供应链可控，可信来源。

```bash
# 搜索股票
npx -y westock-data-skillhub@1.0.3 search 腾讯控股

# 查询K线
npx -y westock-data-skillhub@1.0.3 kline sh600000 --period day --limit 20

```

---

## 已知限制速查

| 限制项 | 说明 |
|--------|------|
| 龙虎榜/大宗交易/融资融券 | 仅支持沪深市场（sh/sz） |
| 筹码成本 | 仅支持沪深京A股（sh/sz/bj） |
| 股东结构 | 仅支持A股和港股 |
| 货币单位 | 港股返回港元/美元，美股返回美元，展示时必须标注正确货币单位，禁止使用人民币符号 |
| `search`/`minute` | 不支持批量查询 |

---

## 批量查询

**所有查询类命令均支持逗号分隔多股代码**。

```bash
npx -y westock-data-skillhub@1.0.3 kline sh600000 --period day --limit 20          # 单股
npx -y westock-data-skillhub@1.0.3 kline sh600000,sh600519 --period day --limit 20 # 批量
```

> `search` 和 `minute` 不支持批量查询。详细返回格式见 [references/ai_usage_guide.md](./references/ai_usage_guide.md)

---

## 核心命令

### 1. 股票搜索

```bash
npx -y westock-data-skillhub@1.0.3 search 腾讯控股          # 搜索股票（默认）
npx -y westock-data-skillhub@1.0.3 search 银行 --sector    # 搜索板块
```

### 2. K线

> 支持个股、指数、板块、ETF

```bash
npx -y westock-data-skillhub@1.0.3 kline sh600000 --period day --limit 20
npx -y westock-data-skillhub@1.0.3 kline hk00700 --period week --limit 10
npx -y westock-data-skillhub@1.0.3 kline sz000001 --period day --limit 60 --fq qfq          # 前复权
npx -y westock-data-skillhub@1.0.3 kline sh600000,sh600519 --period day --limit 20     # 批量
npx -y westock-data-skillhub@1.0.3 kline sh000001 --period day --limit 20               # 指数K线
npx -y westock-data-skillhub@1.0.3 kline pt01801081 --period day --limit 20             # 板块K线
```

**周期**：`day`/`week`/`month`/`season`/`year`（⚠️ 分钟K线不支持，请用 `minute`）

**复权**：默认前复权、`qfq`(前复权)、`hfq`(后复权)、`bfq`(不复权)，最大2000条

### 3. 分时

> 支持个股、指数、板块

```bash
npx -y westock-data-skillhub@1.0.3 minute sh600000        # 1日分时
npx -y westock-data-skillhub@1.0.3 minute sh600000 --days 5      # 5日分时
npx -y westock-data-skillhub@1.0.3 minute sh000001        # 指数分时
npx -y westock-data-skillhub@1.0.3 minute pt01801081      # 板块分时
```

### 4. 财务报表

> 默认返回最新1期，数字参数指定多期

```bash
# A股：lrb(利润表) / zcfz(资产负债表) / xjll(现金流量表)
npx -y westock-data-skillhub@1.0.3 finance sh600000           # 完整财报，最新1期
npx -y westock-data-skillhub@1.0.3 finance sh600000 --num 4         # 完整财报，最近4期
npx -y westock-data-skillhub@1.0.3 finance sh600000 --type lrb --num 8     # 最近8期利润表

# 港股：zhsy(综合损益表) / zcfz / xjll
npx -y westock-data-skillhub@1.0.3 finance hk00700 --num 4

# 美股：income / balance / cashflow
npx -y westock-data-skillhub@1.0.3 finance usBABA --type income --num 4
```

> ⚠️ **货币单位**：港股返回港元/美元，美股返回美元，展示时必须标注正确货币单位

### 5. 公司简况

```bash
npx -y westock-data-skillhub@1.0.3 profile sh600000
npx -y westock-data-skillhub@1.0.3 profile sh600000,hk00700,usAAPL
```

### 6. 资金与交易分析

```bash
# 港股资金
npx -y westock-data-skillhub@1.0.3 hkfund hk00700
npx -y westock-data-skillhub@1.0.3 hkfund hk00700,hk01810 --date 2026-03-10

# A股资金
npx -y westock-data-skillhub@1.0.3 asfund sh600000
npx -y westock-data-skillhub@1.0.3 asfund sh600000,sz000001 --date 2026-03-10

# 美股卖空
npx -y westock-data-skillhub@1.0.3 usfund usAAPL
npx -y westock-data-skillhub@1.0.3 usfund usAAPL,usTSLA --date 2026-03-10

# 龙虎榜（仅沪深）
npx -y westock-data-skillhub@1.0.3 lhb sz000001
npx -y westock-data-skillhub@1.0.3 lhb sz000001 --date 2026-03-20

# 大宗交易（仅沪深）
npx -y westock-data-skillhub@1.0.3 blocktrade sz000001

# 融资融券（仅沪深）
npx -y westock-data-skillhub@1.0.3 margintrade sz000001
```

### 7. 技术指标

```bash
npx -y westock-data-skillhub@1.0.3 technical sh600000                              # 全部指标（最新）
npx -y westock-data-skillhub@1.0.3 technical sh600000 --group macd                         # 特定分组
npx -y westock-data-skillhub@1.0.3 technical sh600000 --group ma,rsi                       # 多分组
npx -y westock-data-skillhub@1.0.3 technical sh600000,hk00700 --group all                  # 批量
npx -y westock-data-skillhub@1.0.3 technical sh600000 --group macd --start 2026-02-01 --end 2026-03-01   # 历史区间
```

**指标分组**：`ma`(均线)、`macd`、`kdj`、`rsi`、`boll`(布林带)、`bias`(乖离率)、`wr`(威廉)、`dmi`(SAR/DMI)、`all`(全部)

### 8. 筹码成本

> ⚠️ 仅支持沪深A股（sh/sz/bj）

```bash
npx -y westock-data-skillhub@1.0.3 chip sh600519
npx -y westock-data-skillhub@1.0.3 chip sh600519 --start 2026-02-01 --end 2026-03-01   # 历史区间
```

### 9. 股东结构

> ⚠️ 仅支持A股和港股

```bash
npx -y westock-data-skillhub@1.0.3 shareholder sh600519     # A股：十大股东、十大流通股东、股东户数
npx -y westock-data-skillhub@1.0.3 shareholder hk00700      # 港股：持股股东+机构持仓
```

### 10. 分红数据

```bash
npx -y westock-data-skillhub@1.0.3 dividend sh600519                              # 最近分红
npx -y westock-data-skillhub@1.0.3 dividend sh600519 --years 5                    # 近5年分红
npx -y westock-data-skillhub@1.0.3 dividend sh600519 --all                        # 含未实施分红方案
npx -y westock-data-skillhub@1.0.3 dividend sh600519,hk00700,usAAPL               # 批量
npx -y westock-data-skillhub@1.0.3 dividend hk00700 --years 10                    # 近10年分红
```

### 11. ETF 基金数据

```bash
npx -y westock-data-skillhub@1.0.3 etf sh510300                  # ETF 详情
npx -y westock-data-skillhub@1.0.3 etf-holdings sh510300         # ETF 持仓明细
npx -y westock-data-skillhub@1.0.3 etf-nav sh510300 --start 2026-01-01 --end 2026-03-31   # ETF 净值历史
npx -y westock-data-skillhub@1.0.3 etf-company sh510300          # ETF 公司信息
npx -y westock-data-skillhub@1.0.3 etf-holders sh510300          # ETF 持有人结构
npx -y westock-data-skillhub@1.0.3 etf-financial sh510300        # ETF 财务指标
```

---

## 平台特色数据

```bash
npx -y westock-data-skillhub@1.0.3 hot stock                  # 热搜股票
npx -y westock-data-skillhub@1.0.3 hot board --limit 10              # 热门板块
npx -y westock-data-skillhub@1.0.3 hot etf                    # 热搜ETF

npx -y westock-data-skillhub@1.0.3 board                      # 热门板块首页

# 投资日历（--limit/--country:1中国2美国3港股/--indicator:1经济2央行3事件4休市）
npx -y westock-data-skillhub@1.0.3 calendar
npx -y westock-data-skillhub@1.0.3 calendar 2026-03-10 --limit 30 --country 1 --indicator 1

npx -y westock-data-skillhub@1.0.3 ipo hs                     # 沪深新股
npx -y westock-data-skillhub@1.0.3 ipo hk                     # 港股新股

npx -y westock-data-skillhub@1.0.3 exdiv sh600519             # 分红除权日历
npx -y westock-data-skillhub@1.0.3 reserve sh600519           # 业绩预告
npx -y westock-data-skillhub@1.0.3 suspension hs              # 停复牌信息
```

---

## 命令速查表

| 命令 | 用途 | 批量 |
|------|------|:----:|
| search | 搜索股票/基金/板块 | ❌ |
| quote | 实时行情 | ✅ |
| kline | K线数据 | ✅ |
| minute | 分时数据 | ❌ |
| finance | 财务报表 | ✅ |
| profile | 公司简况 | ✅ |
| asfund | A股资金流向 | ✅ |
| hkfund | 港股资金流向 | ✅ |
| usfund | 美股卖空数据 | ✅ |
| lhb | 龙虎榜 | ✅ |
| blocktrade | 大宗交易 | ✅ |
| margintrade | 融资融券 | ✅ |
| technical | 技术指标 | ✅ |
| chip | 筹码成本 | ✅ |
| shareholder | 股东结构 | ✅ |
| dividend | 分红数据 | ✅ |
| etf | ETF详情 | ✅ |
| etf-holdings | ETF持仓明细 | ✅ |
| etf-nav | ETF净值历史 | ✅ |
| hot | 热搜/热门板块 | ❌ |
| board | 板块行情 | ❌ |
| calendar | 投资日历 | ❌ |
| ipo | 新股日历 | ❌ |
| exdiv | 分红除权日历 | ✅ |
| reserve | 业绩预告 | ✅ |
| suspension | 停复牌信息 | ❌ |

---

## 股票代码格式

| 市场 | 格式 | 示例 |
|------|------|------|
| 沪市/科创板 | sh + 6位数字 | `sh600000`、`sh688981` |
| 深市 | sz + 6位数字 | `sz000001` |
| 北交所 | bj + 6位数字 | `bj430047` |
| 港股 | hk + 5位数字 | `hk00700` |
| 美股 | us + 代码 | `usAAPL` |

---

## 使用规范

- ✅ 使用 CLI 命令查询数据，命令输出 Markdown 表格，AI 直接从表格中读取数据
- ✅ 查询结果应转为表格或可读格式展示，禁止直接输出原始 JSON
- ❌ 不创建临时脚本文件，不将数据分析逻辑写成独立脚本
- ⚠️ **货币单位**：港股返回港元/美元，美股返回美元，禁止使用人民币符号

---

## 常见分析场景

```bash
# K线分析：提取 volume 计算统计
npx -y westock-data-skillhub@1.0.3 kline sz002714 --period day --limit 20

# 资金流向：解析 MainNetFlow/JumboNetFlow
npx -y westock-data-skillhub@1.0.3 asfund sh688981

# 技术指标：判断金叉/死叉、超买/超卖
npx -y westock-data-skillhub@1.0.3 technical sh600000 --group macd,rsi

# ETF分析：查持仓明细
npx -y westock-data-skillhub@1.0.3 etf sh510300
npx -y westock-data-skillhub@1.0.3 etf-holdings sh510300
```

**完整分析场景参见 [references/scenarios-guide.md](./references/scenarios-guide.md)**

**详细返回格式、字段说明、分析模板参见 [references/ai_usage_guide.md](./references/ai_usage_guide.md)**

---

## 重要声明

> ⚠️ **重要声明**：
>
> 1. 本技能仅提供客观市场数据的查询与展示服务，所有返回数据均来源于公开市场信息，不含任何主观分析、投资评级或交易建议。
> 2. 本技能不构成证券投资咨询服务，使用本技能获取的数据不应作为投资决策的唯一依据。
> 3. 数据可能存在延迟，请以交易所官方数据为准。
> 4. 投资有风险，决策需谨慎。如需专业投资建议，请咨询持牌证券投资顾问机构。

**数据来源**：腾讯自选股数据接口

**适用对象**：金融数据研究人员、量化开发者、投资者教育平台等

---

## 附录：环境安装

**环境要求**：Node.js >= v18

