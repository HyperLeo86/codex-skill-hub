# 两层验证（v0.2）

## Layer A — Structural Gate（check_structure.py）

确定性、可重复、廉价、CI 友好；必须 100% 通过。检查：

- PIR schema 完整性（core_required）
- 字段完整性（claim / evidence / view 必填）
- evidence pointer 有效
- uncertainty 禁止映射（UNKNOWN/UNMEASURED → FAIL 等）
- priority 数量（首屏 critical/important ≤7）
- 重复状态（claim 内容重复）
- 技术字段泄漏到首屏
- 长度限制（summary ≤400 / claims ≤10）
- 数字伪精度（≥3 位小数）
- 空字段 / 非法枚举

它只回答：**是否满足结构性可读规范**。不回答：**人真的觉得好读吗**。

## Layer B — Human Readability Evaluation

验证：快速定位 / 误读 / 理解状态 / 知道下一步 / 知道如何下钻。

来源优先级：

1. 真实使用反馈
2. 人工 3–5 秒测试
3. 未来可选：受控 LLM Judge / A-B Test（v0.2 不引入）

## Common Probe + Task Probe

### Common Probe（所有 Human View）

1. 我现在看到的是什么？
2. 最重要的信息在哪里？
3. 如果需要深入，去哪里看？

### Task Probe

| Task | 探针 |
| --- | --- |
| decide | 当前应该做什么决定？下一步行动是什么？ |
| diagnose | 问题在哪里？下一步怎么处理？ |
| monitor | 什么发生了变化？哪项需要处理？ |
| compare | 最大差异是什么？什么条件下选择 A / B？ |
| browse | 有哪些主要类别 / 选项？下一步最值得展开哪个？ |
| learn | 核心概念是什么？应该沿什么顺序继续理解？ |

## 指标与实验（承接 v0.1 基线）

| 指标 | 目标 |
| --- | --- |
| B1 Time to Orientation 通过率（3–5 秒） | ≥90% |
| B2 关键信息定位时间 | ≤3 秒 |
| B3 误解/误判率 | <10% |
| B4 单报告产出成本 | ≤5 分钟 |
| B5 跨端复用 | 同一 PIR 一次生成 N 端 |

实验：五问探针 A/B → 跨端复用 → 陷阱反测（≥80% 抓取）→ 十倍检验（总时长 ÷10）。
