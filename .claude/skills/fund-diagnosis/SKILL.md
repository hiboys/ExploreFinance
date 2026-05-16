---
name: fund-diagnosis
description: 面向公募基金的单基金综合诊断能力。适用于用户提出“这只基金怎么样”“适不适合继续持有”“风险和收益特征如何”等泛化问题时，返回结构化的Markdown诊断报告。每次仅分析一只基金，不处理多基金对比与量化建模。触发核心条件：用户问法为概括性诊断，未要求具体指标公式计算或回测建模。

---

# 基金综合诊断

通过**自然语言问句**对单只基金进行综合分析，返回 Markdown 诊断报告，适用场景包括：
- **基金整体判断（收益表现 + 风险特征 + 持仓结构）**
- **持有决策参考（继续持有/观望/调整仓位）**
- **波动市场中的基金风险排查**
- **用户泛化问法的一站式诊断回答**


## 功能范围

### 基础诊断能力
- 输入自然语言问句，调用诊基接口生成结构化结论
- 每次仅处理**一只**基金
- 返回可读 Markdown 报告（优先提取 `data.displayData`）
- 支持将结果保存为本地 `.md` 文件，便于复盘追踪

### 触发规则（何时使用本技能）
- 用户问题是**笼统/概括性**诊断：如“这只基金怎么样”“值得继续持有吗”“风险大吗”
- 问句中未明确要求具体指标计算、回测建模或程序化导出
- 若上下文已明确基金实体，用户后续使用“它/这只基金”等代词继续提问，也应触发

### 不触发规则（何时不要使用本技能）
- 用户要求 Python 回测、组合优化、量化建模等高级计算任务
- 用户明确要求导出净值明细、构建CSV或做数据工程处理
- 用户要求多只基金横向对比（应走多标的分析类能力）

### 触发示例

| 触发（泛化诊断） | 不触发（建模/工程） |
|---|---|
| 华夏成长混合基金怎么样？ | 帮我用Python回测华夏成长混合基金策略 |
| 这只基金适合长期持有吗？ | 帮我建一个基金组合优化模型 |
| 它近期风险大吗？ | 把这只基金净值数据导出为CSV |



## 快速开始

### 1. 命令行调用

```bash
python3 {baseDir}/scripts/get_data.py --query "华夏成长混合基金"
```

**输出示例**
```text
Saved: /path/to/workspace/fund_diagnosis/fund_diagnosis_90bf169c.md
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
from scripts.get_data import diagnose_fund

async def main():
    result = await diagnose_fund(
        question="华夏成长混合基金",
        output_dir=Path("workspace/fund_diagnosis"),
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
→ 诊基接口依赖用户自然语言语义，建议避免改写导致意图偏移。

**如何只看输出，不落盘？**
```bash
python3 -m scripts.get_data --query "华夏成长混合基金" --no-save
```

## 合规说明

- 诊断结果仅供参考，不构成投资建议，输出时应附风险提示。
- 禁止在代码或提示词中硬编码账号 ID、会话 ID 或 token。
- 环境变量按敏感信息处理，不在日志或回复中泄露。
- 接口失败时不得编造结论，应返回明确错误或不确定性说明。