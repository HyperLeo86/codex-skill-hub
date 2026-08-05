# 输出规范（world-search-pro）

## report.json 字段

```json
{
  "query": "检索主题",
  "date": "YYYY-MM-DD",
  "type": "现成产品 | 开源库 | 算法/方法 | 数据集 | API/服务 | 教程/技能 | 混合",
  "duration_minutes": 0,
  "constraints": "一句话硬约束",
  "channels": ["exa", "tavily", "内置", "pypi", "github", "实证试跑"],
  "mode": "quick | normal | loop",
  "rounds": 1,
  "history_reused": ["历史库证据"],
  "retrieval_log": [{"variant": "查询词", "engines": ["exa"], "hits": 8, "useful": 3}],
  "verdict_line": "Verdict: <直接用|改改用|只借鉴|淘汰|待验证> — <方案> — <证据>",
  "confidence": "HIGH | MEDIUM | LOW",
  "door": "one-way | two-way",
  "re_evaluation_trigger": "事件/阈值/日期，先到先算",
  "lineage": "为什么是它/以前试过什么（1-3 句）",
  "business_value": "可靠/战略/可适/TCO/速度 的 1-3 句结论",
  "candidates": [
    {
      "name": "", "url": "", "links": {},
      "one_liner": "", "type": "", "maturity": "L0-L5",
      "license_cost": "", "last_update": "", "effort": "",
      "known_issues": "", "verdict_line": "",
      "license_check": "AGPL/GPL/BSL 合规后果",
      "confidence": "HIGH | MEDIUM | LOW", "door": "one-way | two-way",
      "re_evaluation_trigger": "", "lineage": "",
      "match": {"input": "✅", "output": "✅", "scenario": "⚠️", "constraint": "❌"},
      "verdict": "直接用 | 改改用 | 只借鉴 | 淘汰 | 待验证",
      "reason": "", "recommended": false
    }
  ],
  "next_steps": ["最小试跑步骤"],
  "sources": ["真实来源 URL"],
  "unsearched": [],
  "assumptions": []
}
```

## 规则

- candidates ≥1，推荐 3–7 个；recommended 至多 1 个
- verdict 只允许五值；match 只允许 ✅ / ⚠️ / ❌
- 每次 pass 必须有 `verdict_line`；one-way door 必须 HIGH 置信度
- AGPL / GPL / BSL 候选必须填写 `license_check`
- sources 必须真实；无法确认的信息写 known_issues 或 verdict=待验证

## 成熟度 L0–L5

| 级别 | 含义 | 行动 |
|---|---|---|
| L0 | 概念线索，无实现 | 只借鉴 |
| L1 | 论文/方法，无成品 | 只借鉴 |
| L2 | 开源代码，需自己集成 | 可复用 |
| L3 | 可运行工具/API | 首选，试用 |
| L4 | 成熟产品，文档/社区/商业支持 | 直接用 |
| L5 | 事实标准 | 优先遵循 |

## HTML 结构

页头（模式/轮次/时长）→ Pro 决策摘要（Verdict 行/置信度/门/再评估/谱系/业务价值）→ 推荐方案卡 → 候选对比表 → 下一步 → 来源与检索记录。

颜色语义：🟢 直接用 · 🟡 改改用 · 🔵 只借鉴 · 🔴 淘汰 · 🟣 待验证
