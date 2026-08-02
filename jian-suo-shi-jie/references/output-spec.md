# 输出规范

## report.json 字段

```json
{
  "query": "检索主题",
  "date": "YYYY-MM-DD",
  "type": "现成产品 | 开源库 | 算法/方法 | 数据集 | API/服务 | 教程/技能 | 混合",
  "duration_minutes": 0,
  "constraints": "一句话硬约束",
  "channels": ["用过的渠道标签"],
  "mode": "normal | loop",
  "rounds": 1,
  "loop_notes": ["第 1 轮：...", "第 2 轮：..."],
  "candidates": [
    {
      "name": "",
      "url": "官网或主仓库",
      "links": {"GitHub": "https://..."},
      "one_liner": "",
      "type": "",
      "maturity": "L0-L5",
      "license_cost": "",
      "last_update": "",
      "effort": "上手难度",
      "known_issues": "已知坑",
      "match": {"input": "✅", "output": "✅", "scenario": "⚠️", "constraint": "❌"},
      "verdict": "直接用 | 改改用 | 只借鉴 | 淘汰 | 待验证",
      "reason": "一句话理由",
      "recommended": false
    }
  ],
  "next_steps": ["最小试跑步骤"],
  "sources": ["真实来源 URL"],
  "unsearched": ["未覆盖的渠道"],
  "assumptions": ["推测的需求假设"]
}
```

规则：

- candidates 至少 1 个，推荐 3–7 个
- verdict 只允许五个值；recommended 至多一个
- match 四维只允许 ✅ / ⚠️ / ❌
- sources 必须是真实来源；无法确认的信息写入 known_issues 或 verdict=待验证
- 找不到候选时也要写 report.json（candidates 可以为空，结论写明）

## 成熟度定义（离「直接用」有多远）

| 级别 | 含义 | 行动 |
| --- | --- | --- |
| L0 | 概念线索：只有想法/提及，无实现 | 只能借鉴 |
| L1 | 方法论文：有论文/教程/方法，无成品代码 | 只能借鉴 |
| L2 | 代码库：有开源代码，需自己集成 | 可复用，算好集成成本 |
| L3 | 可运行工具：有工具/API/服务，可直接接入 | 首选，直接试用 |
| L4 | 成熟产品：稳定、有文档/社区/商业支持 | 首选，直接用 |
| L5 | 标准生态：事实标准（如 OpenTelemetry） | 优先遵循，不另造 |

## 结果页结构（build_report.py 自动生成）

- 页头：查询主题、日期、类型、耗时、硬约束
- 推荐方案卡：名称、结论、一句话定位、链接、成熟度条、四维匹配、已知坑、理由
- 候选对比表：名称 / 类型 / 成熟度 / 成本 / 一句话 / 结论
- 下一步：最小试跑清单
- 来源与搜索记录：来源链接、未搜索渠道、假设

颜色语义：🟢 直接用 · 🟡 改改用 · 🔵 只借鉴 · 🔴 淘汰 · 🟣 待验证

## 历史库结构

```text
<history-dir>/
  YYYY-MM-DD-主题slug/
    report.json
    report.html
  index.html
```

每次运行 build_report.py 都会重建 index.html（扫描所有子目录的 report.json）。

## build_report.py 用法

```bash
python3 scripts/build_report.py <report.json 路径> [--history-dir <目录>]
```

- report.json 若不在历史目录内，会被复制到历史目录的 `YYYY-MM-DD-主题slug/` 下
- 默认历史目录：`~/Documents/solution-scout-history`
