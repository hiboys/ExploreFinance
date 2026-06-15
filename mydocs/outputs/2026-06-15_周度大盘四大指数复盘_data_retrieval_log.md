# 取数过程记录：周度大盘四大指数复盘

> 执行日期：2026-06-15 | 数据期间：2026-06-08 ~ 2026-06-12 | 基准日：2026-06-05
> 脚本基础路径：`.claude/skills/mx-finance-data/scripts/get_data.py`

---

## 第一轮：行情基石

### 查询 1a：上证指数每日行情

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数，2026-06-08至2026-06-12每日收盘价涨跌幅成交量成交额"`
- **输出数据文件**: [mx_finance_data_c3094a9d.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_c3094a9d.xlsx)
- **输出说明文件**: [mx_finance_data_c3094a9d_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_c3094a9d_description.txt)
- **输出表头**:

| 上证指数(000001.SH) | 2026-06-12(日) | 2026-06-11(日) | 2026-06-10(日) | 2026-06-09(日) | 2026-06-08(日) |
|---|---|---|---|---|---|
| 成交量 | 743.1亿股 | 568.5亿股 | 598.7亿股 | 576.6亿股 | 659.3亿股 |
| 成交额 | 1.537万亿 | 1.186万亿 | 1.227万亿 | 1.173万亿 | 1.267万亿 |
| 涨跌幅 | 1.116% | -0.1555% | -0.4191% | 1.28% | -1.698% |
| 收盘价 | 4031.5129点 | 3987.0147点 | 3993.2258点 | 4010.0307点 | 3959.3378点 |

- **数据行数**: 4
- **计算方法**: 无

### 查询 1b：深证成指/创业板指/科创50 每日行情

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "深证成指、创业板指、科创50，2026-06-08至2026-06-12每日收盘价涨跌幅成交量成交额"`
- **输出数据文件**: [mx_finance_data_e28e07ed.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_e28e07ed.xlsx)
- **输出说明文件**: [mx_finance_data_e28e07ed_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_e28e07ed_description.txt)
- **输出表头**（3 Sheet）:

深证成指:

| 深证成指(399001.SZ) | 2026-06-12(日) | 2026-06-11(日) | 2026-06-10(日) | 2026-06-09(日) | 2026-06-08(日) |
|---|---|---|---|---|---|
| 成交量 | 792.3亿股 | 669.8亿股 | 710.5亿股 | 718.1亿股 | 788.6亿股 |
| 成交额 | 1.678万亿 | 1.366万亿 | 1.392万亿 | 1.467万亿 | 1.525万亿 |
| 涨跌幅 | 0.7503% | -0.6829% | -2.061% | 3.02% | -3.222% |
| 收盘价 | 14963.4073点 | 14851.9751点 | 14954.1008点 | 15268.7147点 | 14821.1861点 |

创业板指:

| 创业板指(399006.SZ) | 2026-06-12(日) | 2026-06-11(日) | 2026-06-10(日) | 2026-06-09(日) | 2026-06-08(日) |
|---|---|---|---|---|---|
| 成交量 | 237.9亿股 | 206.6亿股 | 212.2亿股 | 216.7亿股 | 236.9亿股 |
| 成交额 | 8110亿 | 6543亿 | 6533亿 | 7242亿 | 7273亿 |
| 涨跌幅 | 0.5013% | -1.13% | -2.7% | 3.934% | -3.693% |
| 收盘价 | 3830.353点 | 3811.246点 | 3854.7935点 | 3961.7493点 | 3811.7854点 |

科创50:

| 科创50(000688.SH) | 2026-06-12(日) | 2026-06-11(日) | 2026-06-10(日) | 2026-06-09(日) | 2026-06-08(日) |
|---|---|---|---|---|---|
| 成交量 | 21.02亿股 | 14.22亿股 | 15.91亿股 | 14.1亿股 | 15.71亿股 |
| 成交额 | 1758亿 | 1172亿 | 1391亿 | 1124亿 | 1194亿 |
| 涨跌幅 | 0.04724% | 0.6181% | -0.6545% | 4.168% | -4.302% |
| 收盘价 | 1663.2213点 | 1662.436点 | 1652.2241点 | 1663.1089点 | 1596.5656点 |

- **数据行数**: 12（3 Sheet × 4 行）
- **计算方法**: 无

### 查询 1c：基准日（2026-06-05）收盘价

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，2026-06-05收盘价"`
- **输出数据文件**: [mx_finance_data_3b2d0a54.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_3b2d0a54.xlsx)
- **输出说明文件**: [mx_finance_data_3b2d0a54_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_3b2d0a54_description.txt)
- **输出表头**:

| 收盘价 | 2026-06-05(日) |
|---|---|
| 上证指数(000001.SH) | 4027.7362点 |
| 深证成指(399001.SZ) | 15314.7002点 |
| 创业板指(399006.SZ) | 3957.935点 |
| 科创50(000688.SH) | 1668.3291点 |

- **数据行数**: 4
- **计算方法**: 无

### 二次计算 1：周涨跌幅

- **计算方法**: `周涨跌幅 = (06-12 收盘价 − 06-05 基准日收盘价) ÷ 06-05 基准日收盘价 × 100%`
- **输入列**: 查询 1a/1b 的 06-12 收盘价 + 查询 1c 的 06-05 收盘价
- **计算结果**:

| 指数 | 基准日(06-05) | 最新(06-12) | 周涨跌幅 |
|---|---|---|---|
| 上证指数 | 4027.74 | 4031.51 | +0.09% |
| 深证成指 | 15314.70 | 14963.41 | -2.29% |
| 创业板指 | 3957.94 | 3830.35 | -3.22% |
| 科创50 | 1668.33 | 1663.22 | -0.31% |

---

## 第二轮：技术面 + 估值面 + 两市成交额

### 查询 2a：技术指标（RSI/MACD/MA 四大指数）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，RSI(14)、MACD(12,26,9)、MA5、MA10、MA20、MA60，2026-06-05至2026-06-12"`
- **输出数据文件**: [mx_finance_data_bd4c984a.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_bd4c984a.xlsx)
- **输出说明文件**: [mx_finance_data_bd4c984a_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_bd4c984a_description.txt)
- **输出表头**（06-12 当日关键值）:

| 指标 | 上证指数 | 深证成指 | 创业板指 | 科创50 |
|---|---|---|---|---|
| RSI(14) | 49.42 | 39.21 | 38.95 | 43.78 |
| MACD-DIFF | -28.30 | -60.63 | 24.54 | 8.58 |
| MACD-DEA | -17.35 | 59.55 | 65.90 | 32.16 |
| MACD柱状线 | -21.92 | -240.4 | -82.72 | -47.16 |
| MA5 | 3996 | 14970 | 3854 | 1648 |
| MA10 | — | — | — | 1672 |
| MA20 | 4075 | 15440 | 3962 | 1739 |
| MA60 | 4048 | 14840 | 3673 | 1537 |

- **数据行数**: 29（4 Sheet，各 6~7 行）
- **计算方法**: 无
- **备注**: MA10 仅科创50 返回，上证/深证/创业板均未返回 MA10

### 查询 2b：布林带 — 上证指数

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数，布林带(20,2)，2026-06-05至2026-06-12"`
- **输出数据文件**: [mx_finance_data_6d98db61.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_6d98db61.xlsx)
- **输出说明文件**: [mx_finance_data_6d98db61_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_6d98db61_description.txt)
- **输出表头**（06-12）:

| 指标 | 数值 |
|---|---|
| BOLL-UP | 4151 |
| BOLL-MID | 4028 |
| BOLL-LOW | 3906 |

- **数据行数**: 3
- **计算方法**: 无

### 查询 2c：布林带 — 深证成指

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "深证成指，布林带(20,2)，2026-06-05至2026-06-12"`
- **输出数据文件**: [mx_finance_data_3c38a460.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_3c38a460.xlsx)
- **输出说明文件**: [mx_finance_data_3c38a460_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_3c38a460_description.txt)
- **输出表头**: 仅返回 MID 轨（BOLL布林线 = 15250）
- **数据行数**: 1
- **计算方法**: 无
- **备注**: ⚠️ 仅返回中轨，UP/LOW 缺失

### 查询 2d：布林带 — 创业板指

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "创业板指，布林带(20,2)，2026-06-05至2026-06-12"`
- **输出数据文件**: [mx_finance_data_7efeccb0.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_7efeccb0.xlsx)
- **输出说明文件**: [mx_finance_data_7efeccb0_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_7efeccb0_description.txt)
- **输出表头**（06-12）:

| 指标 | 数值 |
|---|---|
| BOLL-UP | 4294 |
| BOLL-MID | 3945 |
| BOLL-LOW | 3595 |

- **数据行数**: 3
- **计算方法**: 无

### 查询 2e：布林带 — 科创50

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "科创50，布林带(20,2)，2026-06-05至2026-06-12"`
- **输出数据文件**: [mx_finance_data_ae4fc9c6.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_ae4fc9c6.xlsx)
- **输出说明文件**: [mx_finance_data_ae4fc9c6_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_ae4fc9c6_description.txt)
- **输出表头**: 仅返回 MID 轨（BOLL布林线 = 1672）
- **数据行数**: 1
- **计算方法**: 无
- **备注**: ⚠️ 仅返回中轨，UP/LOW 缺失

### 查询 2f：两市每日成交总额

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股每日成交总额，2026-06-08至2026-06-12"`
- **输出数据文件**: [mx_finance_data_c468bebf.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_c468bebf.xlsx)
- **输出说明文件**: [mx_finance_data_c468bebf_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_c468bebf_description.txt)
- **输出表头**:

| 沪深A股 | 06-12 | 06-11 | 06-10 | 06-09 | 06-08 |
|---|---|---|---|---|---|
| 成交额(合计) | 3.215万亿 | 2.552万亿 | 2.619万亿 | 2.640万亿 | 2.793万亿 |

- **数据行数**: 1
- **计算方法**: 无

### 查询 2g：最新交易日 PE/PB

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，PE市盈率、PB市净率，最新"`
- **输出数据文件**: [mx_finance_data_518837c6.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_518837c6.xlsx)
- **输出说明文件**: [mx_finance_data_518837c6_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_518837c6_description.txt)
- **输出表头**（06-12 当日）:

| 指数 | PE(TTM) | PB |
|---|---|---|
| 上证指数 | 17.22倍 | 1.482倍 |
| 深证成指 | 35.30倍 | 2.904倍 |
| 创业板指 | 45.66倍 | 6.006倍 |
| 科创50 | 157.4倍 | 7.355倍 |

- **数据行数**: 8（4 Sheet × 2 行）
- **计算方法**: 无

### 查询 2h：基准日 PE/PB

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "上证指数、深证成指、创业板指、科创50，2026-06-05 PE市盈率、PB市净率"`
- **输出数据文件**: [mx_finance_data_8959efcd.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_8959efcd.xlsx)
- **输出说明文件**: [mx_finance_data_8959efcd_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_8959efcd_description.txt)
- **输出表头**:

| 2026-06-05(日) | 上证指数 | 深证成指 | 创业板指 | 科创50 |
|---|---|---|---|---|
| 市净率PB | 1.479倍 | 2.958倍 | 6.194倍 | 7.366倍 |
| 市盈率PE(TTM) | 17.18倍 | 35.94倍 | 47.09倍 | 157.6倍 |

- **数据行数**: 2
- **计算方法**: 无

### 二次计算 2：ΔPE/ΔPB + 估值-价格联动

- **计算方法**:
  - `ΔPE = PE_最新(06-12) − PE_基准(06-05)`
  - `ΔPE% = ΔPE ÷ PE_基准 × 100%`
  - `ΔPB / ΔPB%` 同理
- **计算结果**:

| 指数 | PE基准 | PE最新 | ΔPE | ΔPE% | PB基准 | PB最新 | ΔPB | ΔPB% | 价格Δ% | 联动解读 |
|---|---|---|---|---|---|---|---|---|---|---|
| 上证 | 17.18 | 17.22 | +0.04 | +0.23% | 1.479 | 1.482 | +0.003 | +0.20% | +0.09% | 估值稳定 |
| 深证 | 35.94 | 35.30 | -0.64 | -1.78% | 2.958 | 2.904 | -0.054 | -1.83% | -2.29% | 杀估值 |
| 创业板 | 47.09 | 45.66 | -1.43 | -3.04% | 6.194 | 6.006 | -0.188 | -3.04% | -3.22% | 杀估值 |
| 科创50 | 157.6 | 157.4 | -0.2 | -0.13% | 7.366 | 7.355 | -0.011 | -0.15% | -0.31% | 轻微杀估值 |

---

## 第三轮：资金面

### 查询 3a：北向资金成交总额

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "北向资金成交总额，2026-06-08至2026-06-12"`
- **输出数据文件**: [mx_finance_data_06b4e66a.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_06b4e66a.xlsx)
- **输出说明文件**: [mx_finance_data_06b4e66a_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_06b4e66a_description.txt)
- **输出表头**:

| 日期 | 北向成交总额(百万) |
|---|---|
| 06-08 | 370,065 |
| 06-09 | 360,933 |
| 06-10 | 349,872 |
| 06-11 | 339,321 |
| 06-12 | 491,028 |

- **数据行数**: 5
- **计算方法**: 无
- **备注**: 2024年起仅披露成交总额，无净买入/沪股通深股通拆分

### 查询 3b：主力净流入合计

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深A股，2026-06-08至2026-06-12，每日超大单净流入、大单净流入、中单净流入、小单净流入、主力净流入"`
- **输出数据文件**: [mx_finance_data_2d5ebe52.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_2d5ebe52.xlsx)
- **输出说明文件**: [mx_finance_data_2d5ebe52_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_2d5ebe52_description.txt)
- **输出表头**:

| 指标 | 06-12 | 06-11 | 06-10 | 06-09 | 06-08 |
|---|---|---|---|---|---|
| 主力净流入资金(合计) | 106.7亿 | -430.5亿 | -1051亿 | 446.8亿 | -1164亿 |

- **数据行数**: 10
- **计算方法**: 无
- **备注**: ⚠️ 四单净流入拆解 API 不支持，此为降级方案，仅返回主力净流入合计

### 查询 3c：融资余额（逐日，含基准日）

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深两市融资余额，2026-06-05、2026-06-08、2026-06-09、2026-06-10、2026-06-11、2026-06-12"`
- **输出数据文件**: [mx_finance_data_1de705f1.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_1de705f1.xlsx)
- **输出说明文件**: [mx_finance_data_1de705f1_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_1de705f1_description.txt)
- **输出表头**:

| 日期 | 06-05 | 06-08 | 06-09 | 06-10 | 06-11 | 06-12 |
|---|---|---|---|---|---|---|
| 融资余额(合计) | 2.756万亿 | 2.731万亿 | 2.736万亿 | 2.728万亿 | 2.722万亿 | 2.723万亿 |

- **数据行数**: 1
- **计算方法**: 无
- **备注**: 今日周一(06-15)，查询上周五(06-12)数据，深交所 T+1 10:00 应已更新

### 查询 3d：融资买入额

- **脚本路径**: `.claude/skills/mx-finance-data/scripts/get_data.py`
- **执行命令**: `python3 .claude/skills/mx-finance-data/scripts/get_data.py --query "沪深两市融资余额，2026-06-08至2026-06-12，每日融资买入额"`
- **输出数据文件**: [mx_finance_data_b1039c6e.xlsx](../../miaoxiang/mx_finance_data/mx_finance_data_b1039c6e.xlsx)
- **输出说明文件**: [mx_finance_data_b1039c6e_description.txt](../../miaoxiang/mx_finance_data/mx_finance_data_b1039c6e_description.txt)
- **输出表头**:

| 日期 | 06-08 | 06-09 | 06-10 | 06-11 | 06-12 |
|---|---|---|---|---|---|
| 融资买入额 | 2266亿 | 2350亿 | 2206亿 | 2160亿 | 2687亿 |

- **数据行数**: 2
- **计算方法**: 无

### 二次计算 3：主力净流入率 + 全周主力净流入合计

- **计算方法**:
  - `主力净流入率 = 主力净流入合计 ÷ 两市成交额 × 100%`
  - `全周主力净流入合计 = Σ 每日主力净流入`
- **计算结果**:

| 日期 | 主力净流入(亿) | 两市成交额(亿) | 主力净流入率 |
|---|---|---|---|
| 06-08 | -1,164 | 27,930 | -4.17% |
| 06-09 | +446.8 | 26,400 | +1.69% |
| 06-10 | -1,051 | 26,190 | -4.01% |
| 06-11 | -430.5 | 25,520 | -1.69% |
| 06-12 | +106.7 | 32,150 | +0.33% |
| **全周** | **-2,092** | — | — |

### 二次计算 4：融资买入占比 + 融资余额周变动

- **计算方法**:
  - `融资买入占比 = 融资买入额 ÷ 两市成交额 × 100%`
  - `融资余额周变动 = 06-12 融资余额 − 06-05 融资余额`
  - `融资余额周变动率 = 周变动 ÷ 06-05 融资余额 × 100%`
- **计算结果**:

| 日期 | 融资买入额(亿) | 两市成交额(亿) | 融资买入占比 |
|---|---|---|---|
| 06-08 | 2,266 | 27,930 | 8.11% |
| 06-09 | 2,350 | 26,400 | 8.90% |
| 06-10 | 2,206 | 26,190 | 8.42% |
| 06-11 | 2,160 | 25,520 | 8.46% |
| 06-12 | 2,687 | 32,150 | 8.36% |

- 融资余额周变动: 27,230 − 27,560 = **−330 亿**（**−1.20%**）

---

## 数据质量总览

| 项目 | 状态 | 备注 |
|---|---|---|
| 有效查询 | 15 次 | 全部成功 |
| 二次计算 | 4 项 | 周涨跌幅、ΔPE/ΔPB、主力净流入率、融资买入占比 |
| 数据缺失 | 2 处 | 深证成指/科创50 布林带仅返回中轨；MA10 仅科创50返回 |
| 降级处理 | 1 处 | 四单净流入拆解 → 主力净流入合计 |
| 异常数据 | 0 | 融资余额全部正常（无 >30% 跳变） |
