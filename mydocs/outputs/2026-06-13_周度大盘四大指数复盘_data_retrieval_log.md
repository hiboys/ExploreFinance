# 取数过程记录：周度大盘四大指数复盘（第二轮）

> **任务**: 周度大盘四大指数复盘，基于最近五个交易日
> **数据源**: mx-finance-data Skill（妙想数据 API）
> **执行时间**: 2026-06-14
> **周定义**: 最近五个交易日（6/8 ~ 6/12），基准日 6/5（第六个交易日）

---

## 查询 1a：上证指数行情数据

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数，2026年6月8日至6月12日每日收盘价涨跌幅成交量成交额"`
- **输出数据文件**: [mx_finance_data_18a9a678.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_18a9a678.xlsx)
- **输出表头**:

| 指标 | 06-08 | 06-09 | 06-10 | 06-11 | 06-12 |
|---|---|---|---|---|---|
| 收盘价 | 3959.34 | 4010.03 | 3993.23 | 3987.01 | 4031.51 |
| 涨跌幅 | -1.70% | +1.28% | -0.42% | -0.16% | +1.12% |
| 成交量 | 659.3亿股 | 576.6亿股 | 598.7亿股 | 568.5亿股 | 743.1亿股 |
| 成交额 | 1.267万亿 | 1.173万亿 | 1.227万亿 | 1.186万亿 | 1.537万亿 |

- **数据行数**: 4

---

## 查询 1b：深证成指/创业板指/科创50 行情

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "深证成指、创业板指、科创50，2026年6月8日至6月12日每日收盘价涨跌幅成交量成交额"`
- **输出数据文件**: [mx_finance_data_247be0e7.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_247be0e7.xlsx)
- **数据行数**: 12（3指数 × 4行）

---

## 查询 2：技术指标（RSI/MACD/均线）

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，RSI(14)、MACD(12,26,9)、MA5、MA10、MA20、MA60，最近五个交易日"`
- **输出数据文件**: [mx_finance_data_5b7d31ee.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_5b7d31ee.xlsx)
- **数据行数**: 29
- **说明**: 含 6/5（基准日）数据，MA10 仅返回上证指数

---

## 查询 3：北向资金成交总额

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "北向资金成交总额，最近五个交易日"`
- **输出数据文件**: [mx_finance_data_e5db1aaa.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_e5db1aaa.xlsx)
- **数据行数**: 6（含 6/5 基准日数据）

---

## 查询 4：估值面 PE/PB

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，PE市盈率、PB市净率，最新"`
- **输出数据文件**: [mx_finance_data_accf4bea.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_accf4bea.xlsx)
- **数据行数**: 8（4指数 × 2指标）

---

## 查询 5：两市成交额

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股每日成交总额，最近五个交易日"`
- **输出数据文件**: [mx_finance_data_f1861147.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_f1861147.xlsx)
- **数据行数**: 1（含 6/5 基准日）

---

## 查询 6：基准日收盘价

- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，2026年6月5日收盘价"`
- **输出数据文件**: [mx_finance_data_38114712.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_38114712.xlsx)
- **数据行数**: 4

---

## 查询 7a-7d：布林带数据（逐指数查询）

| 指数 | 数据文件 |
|---|---|
| 上证指数 | [mx_finance_data_a23c304e.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_a23c304e.xlsx) |
| 深证成指 | [mx_finance_data_ded64059.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_ded64059.xlsx) |
| 创业板指 | [mx_finance_data_b6ea9803.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_b6ea9803.xlsx) |
| 科创50 | [mx_finance_data_eb78ec85.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_eb78ec85.xlsx) |

---

## 查询 8：基准日 PE/PB 估值数据（第三轮新增）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，2026年6月5日 PE市盈率、PB市净率"`
- **输出数据文件**: [mx_finance_data_b3036904.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_b3036904.xlsx)
- **输出数据行**:

| 指标 | 上证指数 | 深证成指 | 创业板指 | 科创50 |
|---|---:|---:|---:|---:|
| 市净率PB | 1.479倍 | 2.958倍 | 6.194倍 | 7.366倍 |
| 市盈率PE(TTM) | 17.18倍 | 35.94倍 | 47.09倍 | 157.6倍 |

- **数据行数**: 2
- **用途**: 与查询 4（最新 PE/PB）对比，计算 ΔPE/ΔPE%/ΔPB/ΔPB%，输出估值-价格联动分析

---

## 查询 9a：主力资金流向（第四轮新增）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股，2026年6月8日至6月12日，每日超大单净流入、大单净流入、中单净流入、小单净流入、主力净流入"`
- **输出数据文件**: [mx_finance_data_41e64af8.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_41e64af8.xlsx)
- **数据行数**: 1（主力净流入合计，未返回四单拆解）
- **数据内容**:

| 日期 | 主力净流入(合计) |
|---|---:|
| 06-08 | −1,164亿 |
| 06-09 | +446.8亿 |
| 06-10 | −1,051亿 |
| 06-11 | −430.5亿 |
| 06-12 | +106.7亿 |

- **说明**: API 未返回超大单/大单/中单/小单拆解的净流入数据（仅返回"流入"且不完整），改用主力净流入合计

## 查询 9b：融资融券数据（第四轮新增）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令 1**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深两市融资余额，2026年6月8日至6月12日，每日融资买入额"`
- **输出数据文件 1**: [mx_finance_data_9b502ba2.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_9b502ba2.xlsx)
- **执行命令 2**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深两市融资余额，2026年6月5日、6月8日、6月9日、6月10日、6月11日、6月12日"`
- **输出数据文件 2**: [mx_finance_data_8c260a97.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_8c260a97.xlsx)
- **执行命令 3**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股，2026年6月5日，融资余额、融资买入额"`
- **输出数据文件 3**: [mx_finance_data_a2d7019e.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_a2d7019e.xlsx)
- **数据行数**: 2（余额 + 买入额）

| 日期 | 融资余额 | 融资买入额 |
|---|---:|---:|
| 06-05（基准） | 2.756万亿 | 2,789亿 |
| 06-08 | 2.731万亿 | 2,266亿 |
| 06-09 | 2.736万亿 | 2,350亿 |
| 06-10 | 2.728万亿 | 2,206亿 |
| 06-11 | 2.722万亿 | 2,160亿 |
| 06-12 | ⚠️ 1.371万亿 | ⚠️ 1,316亿 |

- **说明**: 6/12 数据明显异常（融资余额单日从 2.722→1.371 万亿不可能），判断为数据源未完成更新。报告分析基于 06-05→06-11 可靠区间。

## 查询 9c：四单拆解（尝试，第四轮）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令 1**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股，2026年6月8日至6月12日，每日超大单净流入额、大单净流入额、中单净流入额、小单净流入额"`
- **输出数据文件 1**: [mx_finance_data_1307ac25.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_1307ac25.xlsx)
- **执行命令 2**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股，2026年6月8日、6月9日、6月10日、6月11日、6月12日，每日超大单净流入、大单净流入、中单净流入、小单净流入"` → **返回空**
- **结果**: API 无法返回四单"净流入"拆解；仅返回超大单/中单"流入"（非净），且缺失大单/小单
- **处理**: 报告中仅使用主力净流入合计，标注四单拆解暂不可用

## 二次计算 1：周涨跌幅

- **公式**: (6/12 收盘价 − 6/5 基准日收盘价) ÷ 6/5 基准日收盘价 × 100%
- **基准日**: 2026-06-05（第六个交易日）
- **对比日**: 2026-06-12（第五个交易日）

| 指数 | 6/5 收盘价 | 6/12 收盘价 | 周涨跌幅 |
|---|---|---|---|
| 上证指数 | 4027.74 | 4031.51 | +0.09% |
| 深证成指 | 15314.70 | 14963.41 | -2.29% |
| 创业板指 | 3957.94 | 3830.35 | -3.22% |
| 科创50 | 1668.33 | 1663.22 | -0.31% |

---

## 二次计算 2：估值变化（PE/PB 基准日 vs 最近交易日）

- **公式**: `ΔPE% = (PE_6/12 − PE_6/5) ÷ PE_6/5 × 100%`
- **输入**: 查询 4（6/12 PE/PB）+ 查询 8（6/5 PE/PB）

| 指数 | PE(6/5) | PE(6/12) | ΔPE | ΔPE% | PB(6/5) | PB(6/12) | ΔPB | ΔPB% |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 上证指数 | 17.18 | 17.22 | +0.04 | +0.23% | 1.479 | 1.482 | +0.003 | +0.20% |
| 深证成指 | 35.94 | 35.30 | −0.64 | −1.78% | 2.958 | 2.904 | −0.054 | −1.83% |
| 创业板指 | 47.09 | 45.66 | −1.43 | −3.04% | 6.194 | 6.006 | −0.188 | −3.04% |
| 科创50 | 157.6 | 157.40 | −0.20 | −0.13% | 7.366 | 7.355 | −0.011 | −0.15% |

- **联动结论**: 创业板 → 戴维斯双杀（PE −3.04% + 价格 −3.22%，高度同步）；深证 → 杀估值主导；上证/科创 → 估值稳定

---

## 数据缺失说明

| 缺失项 | 原因 | 处理方式 |
|---|---|---|
| MA10（深证/创业板/科创50） | API 未单独返回 | 以 MA20/Bollinger 中轨作主要中期均线参考 |
| BOLL 需逐指数查询 | 单次查询最多返回一个指数 | 分 4 次查询完成 |
