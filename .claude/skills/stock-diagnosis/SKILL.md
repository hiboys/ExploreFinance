---
name: stock-diagnosis
description: 面向沪深京A股的单票综合诊断能力。适用于用户提出“这只股票整体怎么样”“是否值得继续持有/加仓/减仓”“当前风险和机会如何”等泛化问题时，返回结构化的Markdown诊断报告。每次仅分析一只股票，不处理港股/美股及多标的对比。触发核心条件：用户问法为概括性诊断，未指定某个单一技术指标或财务指标（如MACD、RSI、ROE等）做精确计算。
---

# 股票综合诊断

通过**自然语言问句**对单只A股进行综合分析，返回 Markdown 诊断报告，适用场景包括：
- **个股整体判断（基本面 + 资金面 + 风险面）**
- **持仓决策参考（持有/减仓/止盈/观望）**
- **热点行情下的个股风险排查**
- **用户泛化问法的一站式诊断回答**


## 功能范围

### 基础诊断能力
- 输入自然语言问句，调用诊股接口生成结构化结论
- 每次仅处理**一只**沪深京A股股票
- 返回可读 Markdown 报告（优先提取 `data.displayData`）
- 支持将结果保存为本地 `.md` 文件，便于复盘追踪

### 触发规则（何时使用本技能）
- 用户问题是**笼统/概括性**诊断：如“这只股票怎么样”“值得买吗”“该不该卖”
- 问句中未明确要求计算单个技术指标或财务指标
- 若上下文已明确股票实体，用户后续使用“它/这只股票”等代词继续提问，也应触发

### 不触发规则（何时不要使用本技能）
- 用户明确点名具体指标计算：MACD、KDJ、RSI、布林带、ROE、PE 等
- 用户要求多只股票横向对比（应走多标的分析类能力）
- 用户咨询港股、美股或其他非A股市场

### 触发示例

| 触发（泛化诊断） | 不触发（指标定向） |
|---|---|
| 丹化科技怎么样？ | 丹化科技的MACD出现金叉了吗？ |
| 海康威视亏了怎么操作？ | 海康威视当前市盈率是多少？ |
| 华尔泰值得投资吗？ | 华尔泰的RSI是否超买？ |
| 全面分析一下中国平安 | 中国平安的ROE趋势如何？ |


## 快速开始

### 1. 命令行调用

```bash
python3 {baseDir}/scripts/get_data.py --query "东方财富股票咋样"
```

**输出示例**
```text
Saved: /path/to/workspace/stock_diagnosis/stock_diagnosis_90bf169c.md
（随后输出 Markdown 诊断内容）
```

**参数说明：**

| 参数 | 说明 | 必填 |
|---|---|---|
| `--query` | 用户原始自然语言问句 | ✅（`--query` 或 stdin 二选一） |
| `--no-save` | 仅输出结果，不写入本地文件 | 否 |

### 2. 代码调用

```python
import asyncio
from pathlib import Path
from scripts.get_data import diagnose_stock

async def main():
    result = await diagnose_stock(
        question="分析一下东方财富这只股票",
        output_dir=Path("workspace/stock_diagnosis"),
        save_to_file=True,
    )
    if "error" in result:
        print(result["error"])
    else:
        print(result["content"])
        if result.get("output_path"):
            print("已保存至:", result["output_path"])

asyncio.run(main())
```

## 输出规范
通过脚本或工具拿到诊股结果后，**对用户的可见回复必须以接口返回的 Markdown 正文为主体**，避免模型二次转述。仅当接口/脚本明确返回 `error`、或正文为空时，才用简短文字说明失败原因；**禁止**在失败时杜撰报告内容。

## 常见问题
**为什么需要保持原始问句？**  
→ 诊股接口依赖用户自然语言上下文，建议避免改写导致语义偏移。

**如何只看输出，不落盘？**
```bash
python3 -m scripts.get_data --query "东方财富股票咋样" --no-save
```

## 合规说明

- 诊股结果仅供参考，不构成投资建议，输出时应附风险提示。
- 禁止在代码或提示词中硬编码账号 ID、会话 ID 或 token。
- 环境变量按敏感信息处理，不在日志或回复中泄露。
- 接口失败时不得编造结论，应返回明确错误或不确定性说明。
