---
name: mx-macro-data
description: 基于东方财富数据库，支持自然语言查询全球宏观经济数据，涵盖国民经济核算、价格指数、货币金融、财政收支、对外贸易、就业民生、产业运行等多个领域，适配各类宏观经济研究、市场分析、政策解读等多元专业场景需求。返回结果包含数据说明及 csv 文件。Natural language query for macroeconomic data from financial databases, covering national economic accounting, price indices, monetary finance, fiscal revenue and expenditure, foreign trade, employment, industrial operation, and other fields. It supports diverse scenarios including macroeconomic research, market analysis, and policy interpretation.

---

# 宏观经济数据查询 (mx_macro_data)

通过**文本输入**查询宏观经济数据，接口返回 JSON 后会自动转换为 **CSV** 并生成对应的**内容描述 txt** 文件。


## ⚠️ 核心输入约束 (Critical Input Constraints)

- **时间维度**：支持相对时间表述（如“今年”、“过去三年”、“上月”）。
- **地域维度**：支持宏观地区表述（如“中国”、“美国”、“欧元区”、“华东地区”、“中国各省”），无需拆解为具体省市列表。

### 1. 禁止模糊商品类别 (No Ambiguous Commodities)
- **禁止输入**：大类统称（如“稀土金属”、“有色金属”、“农产品”、“能源”、“科技股”）。
- **要求**：必须解包为具体的**交易品种名称或代码**。
  - ❌ 错误：`"查询稀土价格走势"`
  - ✅ 正确：`"查询氧化镨钕、氧化镝、氧化铽的价格走势"`

### 2. 禁止宏观泛指指标 (No Macro Generalizations without Metrics)
- **禁止输入**：宽泛的经济概念而无具体指标（如“中国经济”、“美国制造业状况”、“全球通胀情况”）。
- **要求**：必须指定具体的**指标名称**（如 GDP、CPI、PMI、失业率、工业增加值等）。
  - ❌ 错误：`"查询中国经济数据"`
  - ✅ 正确：`"查询中国 GDP 同比增速、中国 CPI 同比"`
  - ✅ 正确：`"查询美国制造业 PMI"` (地域允许宏观，但指标必须具体)

### 3. 时间与地域的灵活性 (Flexible Time & Region)
- **时间**：无需绝对日期。
  - ✅ 允许：`"查询中国过去五年的M2增速"`、`"查询上个月美国的非农数据"`、`"查询黄金今日价格"`。
  - ✅ 允许（缺省）：`"查询德国失业率"` 。
- **地域**：无需拆解为子集列表。
  - ✅ 允许：`"查询华东地区GDP"`,`"查询中国各省GDP"`。
  - ⚠️ 注意：若涉及“主要新兴市场”、“Top 5 国家”等动态排名指代，仍建议上层模型解包为具体国家列表（如 `"查询中国、印度、巴西的M2"`），以确保数据源一致性。

## 🔄 输出接口与上层规划协议 (Output Interface & Orchestration Protocol)

本 Skill 仅负责执行单次查询并生成文件。**为实现数据完整性保障，上层规划引擎必须根据以下协议，对本 Skill 的输出进行后续处理。**

### 1. 输出文件结构 (Output File Structure)
执行 `mx_macro_data` 后，Skill 将在指定目录下生成一个或多个 CSV 文件，以及一个描述文件。

- **CSV 文件**：`mx_macro_data_<查询ID>_<频率>.csv`
  - *示例*：`mx_macro_data_4591GG28_yearly.csv`, `mx_macro_data_4591GG28_quarterly.csv`, `mx_macro_data_4591GG28_monthly.csv`
  - **注意**：文件数量和频率取决于查询指标的可用性（yearly、quarterly、monthly、weekly、daily）。
- **描述文件**：`mx_macro_data_<查询ID>_description.txt`
  - 包含数据来源、时间范围、指标说明等基础信息。

### 2. 上层规划引擎必须执行的“完整性复核”逻辑 (Mandatory Verification Logic for Orchestrator)

上层规划引擎在调用 `mx_macro_data` 后，**必须**执行以下工作流，以确保最终结果的完整性：
#### **阶段 A: 任务解析与预期规划 (Task Parsing & Expectation Planning)**
1.  **解析原始用户意图**：从用户查询中提取核心要素。
2.  **构建预期全集 (Expected Universe)**：
    - **地域**：通过规划引擎的内置知识库、搜索引擎或 LLM 推理能力，将模糊地域表述解析为具体行政单元。例如："中国各省" → 34 个省级行政区；"华东地区" → 上海、江苏、浙江、安徽、福建、江西、山东共 7 个省市。
    - **指标**：将复合指标拆解为独立指标。例如："GDP, CPI" → ["GDP", "CPI"]。
    - **频率**：根据查询语境推断预期频率，可能生成多个频率的数据文件（yearly、quarterly、monthly等）。

#### **阶段 B: 文件读取与差异检测 (File Reading   & Gap Detection)**
1.  **获取输出文件列表**：获取 `mx_macro_data` 生成的所有 CSV 文件路径。
2.  **读取并分析每个文件**：
    - 使用规划引擎内置的代码执行能力（如 Python Sandbox）读取 CSV。
    - 提取每个文件中实际覆盖的 `(地区, 指标)` 组合及其数量。
3.  **执行差异计算**：
    - 对**每一种频率**的文件，分别计算 `Missing_Pairs_<Frequency> = Expected_Universe - Actual_From_CSV_File`。
    - 识别出具体缺失的项（如：年频数据中缺失“西藏-GDP”）。

#### **阶段 C: 决策与迭代调用 (Decision & Iterative Invocation)**

> ⚠️ **强制要求**：上层规划引擎**必须**执行以下补全流程，不得在存在缺失数据时直接交付结果。

1.  **判断是否需要补全**：
    - 如果所有频率的 `Missing_Pairs` 集合均为空：**结束流程**，交付现有文件。
    - 如果存在非空的 `Missing_Pairs` 集合：**必须进入补全流程**，不可跳过。

2.  **构建补全查询**：
    - 根据 `Missing_Pairs_<Frequency>` 中的缺失项，结合原始查询的时间维度，构造新的自然语言查询。
    - **示例**：
      ```
      Missing_Pairs_季 = [("西藏", "GDP"), ("宁夏", "GDP")]
      ↓
      补全查询 = "查询西藏自治区、宁夏回族自治区的 GDP 季度数据，时间范围同前次查询"
      ```

3.  **再次调用 `mx_macro_data`**：
    - 使用新构造的补全查询，再次调用本 Skill 获取缺失数据。

4.  **迭代循环**：
    - 重复执行 **阶段 B（差异检测）→ 阶段 C（决策补全）**，直至满足以下任一条件：
      - ✅ 所有频率下的缺失项均已补全
      - ⚠️ 达到最大重试次数5次，此时应向用户报告未能补全的数据项

#### **阶段 D: 最终交付 (Final Delivery)**
1.  **数据合并（可选）**：
    - 如果需要，可将同一频率下多次查询的结果（如多个 `quarterly.csv` 文件）合并为一个完整的 `quarterly.csv`。
2.  **状态报告**：
    - 规划引擎应向上游（如用户界面）报告最终交付的文件列表，并可选地报告补全过程（如“系统已自动补全 2 个缺失数据项”）。
---

## 功能范围

### 基础查询能力

- **经济指标**：GDP、CPI、PPI、PMI、失业率、工业增加值等（支持指定国家/地区及具体指标名）。
- **货币金融**：M1/M2 货币供应量、社融规模、国债利率、汇率（支持指定币种对）。
- **商品价格**：黄金、白银、原油、铜、特定稀土氧化物等（**必须**指定具体品种）。
- **时间频率**：自动识别相对时间（年、季、月、周、日）并匹配对应频率数据；若未指定，返回最新数据。

### 查询示例对照表

| 类型     | ❌ 禁止的模糊查询 (指标/品种不明)      | ✅ 允许的明确查询 (时间/地区可灵活)             |
|----------|--------------------------------------|------------------------------------------------|
| 国内经济 | 查询华东地区GDP                        | 查询华东地区 GDP                              |
| 货币供应 | 查询主要新兴市场货币供应                | 查询中国、印度、巴西的 M2 货币供应量             |
| 商品价格 | 查询稀土和有色金属价格                 | 查询氧化镨钕、铜、铝的现货价格走势                |
| 全球宏观 | 查询 Top 3 经济体非农数据              | 查询美国、中国、德国的非农就业数据                |
| 时间灵活 | (无)                                  | 查询美国过去十年的失业率趋势                    |
| 默认时间 | (无)                                  | 查询日本最新的核心 CPI 数据                     |



## 快速开始

### 1. 命令行调用

在项目根目录或配置的工作目录下执行：

```bash
python3 {baseDir}/scripts/get_data.py --query 中国GDP
```
**参数说明：**

| 参数            | 说明             | 必填 |
| --------------- | ---------------- | ---- |
| `--query`       | 自然语言查询条件 | ✅    |
```
### 2. 代码调用

```python
import asyncio
from pathlib import Path
from scripts.get_data import query_mx_macro_data

async def main():
    result = await query_mx_macro_data(
        query="中国近五年GDP",
        output_dir=Path("workspace/mx_macro_data"),
    )
    if "error" in result:
        print(result["error"])
    else:
        print(f"CSV: {r['csv_paths']}")
        print(f"描述: {r['description_path']}")
        print(f"行数: {r['row_counts']}")

asyncio.run(main())
```

输出示例：
```
CSV: /path/to/workspace/mx_macro_data/mx_macro_data_4591GG28_yearly.csv
CSV: /path/to/workspace/mx_macro_data/mx_macro_data_4591GG28_quarterly.csv
CSV: /path/to/workspace/mx_macro_data/mx_macro_data_4591GG28_monthly.csv
描述:/path/to/workspace/mx_macro_data/mx_macro_data_4591GG28_description.txt
行数: 年: 10行, 季: 20行, 月: 40行
```

## 输出文件说明

| 文件 | 说明 |
|------|------|
| `mx_macro_data_<查询ID>_<频率>.csv` | 按频率分组的宏观数据表，UTF-8 编码，可直接用 Excel 或 pandas 打开。 |
| `mx_macro_data_<查询ID>_description.txt` | 说明文件，含各频率数据统计、数据来源和单位等信息。 |

## 环境变量

| 变量                      | 说明                                  | 默认                     |
| ------------------------- | ------------------------------------- | ------------------------ |
| `MX_MACRO_DATA_OUTPUT_DIR` | CSV 与描述文件的输出目录（可选）      | `workspace/mx_macro_data` |

## 常见问题

### 用户常见问题
A: 通过设置 `MX_MACRO_DATA_OUTPUT_DIR` 环境变量：
```bash
export MX_MACRO_DATA_OUTPUT_DIR="/path/to/output"
python3 scripts/get_data.py --query "查询内容"
```

### 开发者常见问题（规划引擎集成）

**Q: 为什么需要上层规划引擎做复核？**

A: 本 Skill 专注于单一查询能力，不负责数据完整性校验。完整性验证（如"中国各省"是否真的覆盖全部省份）属于业务逻辑范畴，更适合由具备上下文理解和决策能力的规划引擎来处理。

**Q: 如何判断何时进行复核？**

A: 当原始用户意图包含以下特征时，应自动触发复核流程：
- **集合性词汇**：如"各省"、"各地区"、"华东地区"等
- **多指标查询**：如"GDP 和 CPI"、"主要经济指标"等

**Q: 如何处理不同频率的数据？**
A: **必须**对每种频率的 CSV 文件**分别**执行完整性审计和补全。年频数据的缺失不能用月频数据补全，反之亦然。