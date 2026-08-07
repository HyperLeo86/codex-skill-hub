---
name: world-search-pro
license: MIT
description: 动手前的方案侦察 + 决策 + 归档完整流水线：多引擎检索、六层选型、业务价值与许可硬检查、谱系解释、Verdict 行与置信度、报告归档。当用户说 「帮我找找有没有现成的方案」；「这个需求世界上已经有人做了吗」；「不要重复造轮子，先检索世界」；「选型：这几个方案该用哪个」；「build vs buy 帮我分析一下」；「我想做 X，先看看有没有现成的库/产品/API」；「这个技术方案以前试过吗」 时使用；不用于：市场调研/创业立项/竞品分析、创意头脑风暴、纯 bug 修复或重构、用户已完全指定方案的脚本任务。
---

# world-search-pro

**版本**：1.1（2026-08-07）

## 概览

动手前的方案侦察 + 决策 + 归档完整流水线：多引擎检索、六层选型、业务价值与许可硬检查、谱系解释、Verdict 行与置信度、报告归档

## 触发与反触发

- 触发：帮我找找有没有现成的方案；这个需求世界上已经有人做了吗；不要重复造轮子，先检索世界；选型：这几个方案该用哪个；build vs buy 帮我分析一下；我想做 X，先看看有没有现成的库/产品/API；这个技术方案以前试过吗
- 反触发：市场调研/创业立项/竞品分析；创意头脑风暴；纯 bug 修复或重构；用户已完全指定方案的脚本任务

## 决定权（自由度 medium）

- 按伪代码/模板执行，参数可依上下文调整
- 输出格式遵循 references/output-spec.md，内容允许合理变化
- 报告渲染以 scripts/build_report_pro.py 为准，禁止手工覆盖脚本输出

## 运行模式

- Quick：单点明确需求，≤15 分钟，只输出 Verdict 行 + 3 个候选（走步骤 0→1→3→4→7，跳过 2/5/6/8/9/10/11）
- Full（默认）：完整流水线，≤2 小时，产出 report.json + report.html
- Loop：深扫/对标，2–3 轮；一轮新增有用候选 <2 提前停止，≤3 小时。「对标」指对具体方案/技术的深度扫描与替代对比；不用于竞品全景分析（那是市场调研）

## 工作流（Full 模式 12 步）

跨切面规则（不占步骤号）：上下文保护——Full 模式原始检索输出进子代理/临时文件，主上下文只留摘要；生效于步骤 3–9，不是归档后的顺序步骤。

0. **Preflight + articulate**：检查渠道可用性（缺失必须记录）；先输出用户可见三行：What / Language+Framework / Constraints
1. **需求翻译 + 术语地图**：确认方案类型与硬约束；每核心概念生成 3–5 个变体查询（中英/口语/学术/反搜）
2. **历史库回灌**：浏览历史 index.html 与 */report.json，同主题证据标注「历史库」直接进候选
3. **三引擎扫描**：Exa（scripts/exa_search.py）主引擎 + Tavily（scripts/tavily_search.py）交叉验证 + 内置/渠道矩阵（references/channels.md）；结果按 URL 去重合并
4. **六层选型**：REUSE → USE → FORK → BUY → INTEGRATE → BUILD，逐层记录引用（channels.md）；BUILD 落到「大概率无现成方案 + 自建理由」，不占五结论
5. **评估**：六维（功能/维护/社区/文档/许可/依赖）+ 业务价值五维（可靠/战略/可适/TCO/速度）+ 反偏见（≥3 独立来源）+ 许可/CVE 硬检查
6. **谱系解释**：按 references/lineage.md 补「为什么是它/以前试过什么」
7. **决策**：五结论 + Verdict 行 + 置信度（HIGH/MEDIUM/LOW）+ 门类型（one-way/two-way）+ 再评估触发器
8. **最小试跑**：首选 5 分钟文档 → 15 分钟真实运行 → 10 分钟查评价；失败则降级「待验证」
9. **输出归档**：report.json + report.html（output-spec.md / build_report_pro.py）
10. **（跨切面）上下文保护**：Full 模式原始检索输出进子代理/临时文件，主上下文只留摘要；生效于步骤 3–9，非顺序步骤
11. **账本回灌**：失败写 references/regressions.md；命中旧失败必须有防复发条款

## 决策模型

| 五结论 | 六层映射 | 动作 |
|---|---|---|
| 直接用 | REUSE / USE / BUY / INTEGRATE | 安装即用 |
| 改改用 | FORK / EXTEND / COMPOSE | 包装/分叉/组合 |
| 只借鉴 | reference（思路复用） | 只取思路 |
| 淘汰 | 硬约束不满足 | 不进候选 |
| 待验证 | 信息不足 | 试跑或人工确认 |

BUILD = 自建（结论标注「自建合理」）。

**Verdict 行**（每次 pass 必出）：

```
Verdict: <直接用|改改用|只借鉴|淘汰|待验证> — <方案> — <证据（版本/日期/许可/实测），禁止形容词>
```

## 验收

- 每次 pass 输出一行可执行的 Verdict 行
- 每个推荐结论能指回真实来源；AGPL/GPL/BSL 必须显式写出合规后果
- report.json 含 retrieval_log、lineage、confidence、re_evaluation_trigger
- one-way door 必须 HIGH 置信度，否则不得给「直接用」
- 首选必须最小试跑（无法跑 → 降级待验证）

## 失败降级

- 多引擎不可用 → 内置搜索 + 渠道矩阵，检索日志标注缺失渠道
- 全部零候选 → 换查询再扫一轮；仍无 → 「大概率无现成方案」+ 自建理由
- 用户说「别查了」→ 输出跳过式 Verdict 后继续，不执行完整流程
- 试跑失败 → 结论降级待验证，标注失败原因，不编造成功

## 停止规则

- L4 且四维匹配 → 直接最小试跑，不再扩展候选
- 一轮新增有用候选 <2 → 提前停止（Loop）
- 超时上限：Quick ≤15 分钟 / Full ≤2 小时 / Loop ≤3 小时

## 资源

- scripts/exa_search.py、scripts/tavily_search.py：三引擎检索
- scripts/build_report_pro.py：Pro 报告渲染
- references/channels.md：渠道矩阵与六层选型
- references/domain.md：dev/writing/data/ops 领域模式
- references/output-spec.md：report.json 扩展字段与 HTML 结构
- references/lineage.md：谱系追踪技法
- references/validation.md：A/B 协议与评估指标
- references/regressions.md：失败账本（升级前全量回归）

## Token 预算

SKILL.md ≤280 行 / ≤2500 token；references 按需加载，单文件 ≤10k 词；description ≤1024 字符。
