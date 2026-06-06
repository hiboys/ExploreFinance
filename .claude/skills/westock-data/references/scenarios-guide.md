# WeStock Data - 常见分析场景详解

> **定位**：本文档是 SKILL.md 的 **L3 层补充材料**，提供完整的分析场景示例和详细操作步骤。
>
> **使用方式**：AI 在遇到不确定的分析场景时按需加载本文档。命令列表和基本用法请参见
> [SKILL.md](../SKILL.md)。

---

## 一、基础查询场景

### 场景 1：分析成交量趋势

```
用户："分析牧原股份近20天的成交量"
→ npx -y westock-data-skillhub@1.0.3 search 牧原股份 → npx -y westock-data-skillhub@1.0.3 kline sz002714 --period day --limit 20 → 从表格中提取volume → 计算统计指标 → 输出分析报告
```

### 场景 2：财务分析

```
用户："分析贵州茅台的盈利能力"
→ npx -y westock-data-skillhub@1.0.3 finance sh600519 → 提取关键指标 → 计算同比/环比 → 输出分析结论
```

---

## 二、资金分析场景

### 场景 3：批量资金流向分析

```
用户："对比腾讯和美团的资金流向"
→ npx -y westock-data-skillhub@1.0.3 hkfund hk00700,hk03690 --date 2026-03-10 → 一次查询两只 → 解析批量查询结果 → 对比资金面
```

### 场景 4：A股资金流向分析

```
用户："分析中芯国际的资金面"
→ npx -y westock-data-skillhub@1.0.3 asfund sh688981 → 解析 MainNetFlow/JumboNetFlow → 输出资金面判断
```

### 场景 5：港股资金分析

```
用户："腾讯控股的资金流向情况"
→ npx -y westock-data-skillhub@1.0.3 hkfund hk00700 → 解析 TotalNetFlow/ShortRatio/LgtHoldInfo → 输出资金分析
```

---

## 三、指数与板块场景

### 场景 6：板块资金流向分析

```
用户："半导体板块的资金流向情况"
→ npx -y westock-data-skillhub@1.0.3 search 半导体 --sector → 获取 pt01801081
→ npx -y westock-data-skillhub@1.0.3 quote pt01801081 → 输出板块行情分析
```

### 场景 7：多指数对比

```
用户："对比沪深两市今天的表现"
→ npx -y westock-data-skillhub@1.0.3 quote sh000001,sz399001 → 解析批量查询结果 → 对比涨跌幅 → 输出分析
```

### 场景 8：板块行情分析

```
用户："半导体板块今天的涨跌情况"
→ npx -y westock-data-skillhub@1.0.3 search 半导体 --sector → 获取 pt01801081 → npx -y westock-data-skillhub@1.0.3 quote pt01801081 → 展示涨跌幅和成交额
```

### 场景 8.1：指数/板块K线分析

```
用户："上证指数近一个月的走势"
→ npx -y westock-data-skillhub@1.0.3 kline sh000001 --period day --limit 30 → 解析K线数据 → 计算区间涨跌幅 → 输出趋势分析

用户："半导体板块近一周的K线走势"
→ npx -y westock-data-skillhub@1.0.3 search 半导体 --sector → 获取 pt01801081
→ npx -y westock-data-skillhub@1.0.3 kline pt01801081 --period day --limit 5 → 解析K线 → 输出走势
```

### 场景 8.2：指数/板块分时走势

```
用户："大盘今天的分时走势怎么样"
→ npx -y westock-data-skillhub@1.0.3 minute sh000001 → 解析分时数据 → 输出走势分析

用户："半导体板块今天的盘中走势"
→ npx -y westock-data-skillhub@1.0.3 search 半导体 --sector → 获取 pt01801081
→ npx -y westock-data-skillhub@1.0.3 minute pt01801081 → 解析分时 → 输出走势
```

### 场景 9：跨市场指数对比

```
用户："对比恒生指数和纳斯达克今天的表现"

AI 步骤：
1. 批量查询行情：npx -y westock-data-skillhub@1.0.3 quote hkHSI,us.IXIC
2. 分别解析各指数的行情数据
3. 对比涨跌幅
4. 输出跨市场指数对比分析
```

---

## 四、平台特色数据场景

### 场景 10：行业板块分析

```
用户："今天哪些行业板块涨得好？资金在流向哪里？"

AI 步骤：
1. 查询板块首页：npx -y westock-data-skillhub@1.0.3 board
   → 格式化输出行业/概念/地域板块资金流向（净流入TOP和净流出TOP）、北向资金热门板块（当日/近5日/近20日）
2. 直接基于格式化输出，输出行业板块资金面和涨幅分析
```

### 场景 11：投资日历查询

```
用户："本周有哪些重要的财经事件？"

AI 步骤：
1. 查询有事件的日期：npx -y westock-data-skillhub@1.0.3 calendar
   → 格式化输出月历视图，★ 标记有事件的日期
2. 从月历中筛选本周日期
3. 逐日查询事件详情：npx -y westock-data-skillhub@1.0.3 calendar 2026-03-10 --limit 30
   → 格式化输出事件列表（按重要性排序），含星级、时间、国家、内容、前值/预测/实际值
4. 可按地区筛选：npx -y westock-data-skillhub@1.0.3 calendar 2026-03-10 --limit 30 1  // 仅中国
5. 可按指标筛选：npx -y westock-data-skillhub@1.0.3 calendar 2026-03-10 --limit 30 --country 1 --indicator 1  // 仅经济数据
6. 直接基于格式化输出，输出本周财经事件日历
```

### 场景 12：新股申购分析

```
用户："最近有什么新股可以申购？"

AI 步骤：
1. 查询沪深新股：npx -y westock-data-skillhub@1.0.3 ipo hs
   → 格式化输出按状态分类（即将发行/今日可申购/即将上市/中签号公布/已上市），含发行价、市盈率、申购代码、上市日、可比公司、风险提示等
2. 可选：查询港股新股：npx -y westock-data-skillhub@1.0.3 ipo hk
   → 格式化输出按申购日/上市日分类，含入场费、认购倍数、募集金额等
3. 可选：查询美股新股：npx -y westock-data-skillhub@1.0.3 ipo us
   → 格式化输出按状态分组（注册中/已定价/已提交等），含行业、发行价、价格区间、承销商等
4. 可选：指定查询天数：npx -y westock-data-skillhub@1.0.3 ipo hs --days 60
5. 直接基于格式化输出，输出新股申购机会分析
```

---

## 五、深度分析场景

### 场景 13：筹码成本分析

```
用户："分析一下茅台的筹码分布情况"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 贵州茅台 → sh600519
2. 查询筹码数据：npx -y westock-data-skillhub@1.0.3 chip sh600519
3. 解析筹码盈利率（chipProfitRate）→ 判断获利盘/套牢盘比例
4. 对比收盘价与平均成本（chipAvgCost）→ 判断当前价位相对筹码成本的位置
5. 分析集中度（chipConcentration90/70）→ 集中度越低，筹码越集中
6. 输出筹码分析结论
```

### 场景 14：筹码趋势分析

```
用户："看看招商银行近一个月的筹码变化趋势"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 招商银行 → sh600036
2. 查询历史筹码：npx -y westock-data-skillhub@1.0.3 chip sh600036 --start 2026-02-10 --end 2026-03-10
3. 解析 items[] 中每日的筹码数据
4. 分析趋势：
   - 盈利率趋势（上升 = 获利盘增加）
   - 平均成本趋势（上升 = 筹码成本抬升，主力可能在建仓）
   - 集中度趋势（下降 = 筹码趋于集中，可能有主力控盘）
5. 输出筹码变化趋势分析
```

### 场景 15：股东研究分析

```
用户："查一下茅台的十大股东"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 贵州茅台 → sh600519
2. 查询股东数据：npx -y westock-data-skillhub@1.0.3 shareholder sh600519
3. 解析 top10Shareholders（十大股东）和 top10FloatShareholders（十大流通股东）
4. 解析 shareholderNum（股东户数）→ 总户数/A股户数/环比变动/户均持股
5. 分析持股集中度、机构/个人占比、持股变动趋势
6. 输出股东结构分析报告
```

### 场景 16：港股股东与机构持仓分析

```
用户："腾讯的机构持仓情况怎么样？"

AI 步骤：
1. 查询股东数据：npx -y westock-data-skillhub@1.0.3 shareholder hk00700
2. 解析 shareholderInfo（持股股东）→ 主要股东持股比例
3. 解析 shareholderDist（股东分布）→ 各类机构持股情况
4. 解析 instHoldingStats（机构持仓统计）→ 机构数量变化、增减持趋势
5. 输出机构持仓分析
```

### 场景 17：分红数据分析

```
用户："贵州茅台的分红情况如何？"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 贵州茅台 → sh600519
2. 查询分红数据：npx -y westock-data-skillhub@1.0.3 dividend sh600519
3. 解析分红明细（reportEndDate, dividendFlag, procedure, dividendPlan, cashDiviRMB 等）
4. 注意：A股分红数据为"每10股派息"（cashDiviRMB）
5. 输出分红情况分析
```

### 场景 18：跨市场分红对比

```
用户："对比腾讯和苹果的分红情况"

AI 步骤：
1. 批量查询分红数据：npx -y westock-data-skillhub@1.0.3 dividend hk00700,usAAPL
2. 解析批量查询结果 中各股票的分红方案
3. 对比两只股票的分红记录
4. 输出跨市场分红对比分析
```

### 场景 19：A股分红历史查询

```
用户："查看贵州茅台近5年的分红记录"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 贵州茅台 → sh600519
2. 查询分红历史：npx -y westock-data-skillhub@1.0.3 dividend sh600519 --years 5
3. 解析 plans[] 中的分红方案（reportEndDate, cashDiviRMB, dividendPlan）
4. 注意：A股分红数据为"每10股派息"（cashDiviRMB）
5. 分析每年分红趋势（分红金额、分红频次、股利支付率变化）
6. 输出分红历史趋势分析
```

### 场景 20：港股分红历史查询

```
用户："查看腾讯近几年的分红记录"

AI 步骤：
1. 查询分红历史：npx -y westock-data-skillhub@1.0.3 dividend hk00700 --years 5
2. 解析 plans[] 中的分红方案
3. 分析每年分红趋势（每股派息、合计派现、分红频次）
4. 输出分红历史趋势分析
```

### 场景 21：分红历史自定义年数

```
用户："查看苹果近10年的分红记录"

AI 步骤：
1. 查询分红历史：npx -y westock-data-skillhub@1.0.3 dividend usAAPL --years 10
2. 解析 plans[] 中的分红方案
3. 分析美股季度分红特征（每季度分红金额、年度累计）
4. 注意：美股可能包含 splitInfo（拆合股信息）
5. 输出长期分红趋势分析
```

### 场景 22：跨市场分红历史对比

```
用户："对比贵州茅台、腾讯和苹果近3年的分红情况"

AI 步骤：
1. 批量查询分红历史：npx -y westock-data-skillhub@1.0.3 dividend sh600519,hk00700,usAAPL --years 3
2. 解析批量查询结果 中各股票的 plans[]
3. 注意各市场数据格式差异：
   - A股：cashDiviRMB（每10股派息，元）
   - 港股：cashDivPerShare（每股派息，港元）
   - 美股：dividend（每股分红，美元）
4. 统一换算为每股派息金额进行对比
5. 输出跨市场分红对比分析
```

### 场景 23：财报披露日查询

```
用户："茅台什么时候发财报？"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 贵州茅台 → sh600519
2. 查询业绩预告：npx -y westock-data-skillhub@1.0.3 reserve sh600519
3. 解析 items[] 中的披露日列表
4. 区分已披露（isPredicted=false）和预约披露（isPredicted=true）
5. 输出最近的财报披露日历
```

### 场景 24：分红除权日查询

```
用户："苹果什么时候除权派息？"

AI 步骤：
1. 搜索股票：npx -y westock-data-skillhub@1.0.3 search 苹果 → usAAPL
2. 查询分红除权日：npx -y westock-data-skillhub@1.0.3 exdiv usAAPL
3. 解析 items[] 中的除权日列表
4. 展示每次的除权日、支付日、每股分红
5. 输出分红除权日历
```

---

**记住**：npx -y westock-data-skillhub@1.0.3 是数据查询工具，AI 负责数据分析和洞察！
