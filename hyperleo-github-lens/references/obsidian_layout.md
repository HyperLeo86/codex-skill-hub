# Obsidian 三件套布局（hyperleo-github-lens）

## Vault 定位

优先级：环境变量 `OBSIDIAN_VAULT` → `~/Library/Application Support/obsidian/obsidian.json` 中 `open:true` 的仓库 → 第一个仓库。由 `scripts/obsidian_locate.sh` 输出，找不到则降级到 `outputs/obsidian-export/`。

## 目录结构

```text
<Vault>/GitHub 项目分析/
├── GitHub 项目分析看板.md      # 看板：汇总 + 全部项目入口
├── _模板/
│   ├── 简页模板.md
│   └── 深入分析模板.md
└── <owner-repo>/
    ├── <owner-repo>-简页.md
    └── <owner-repo>-深入分析.md
```

## 看板（GitHub 项目分析看板.md）

frontmatter：

```yaml
---
type: github-lens-dashboard
updated: YYYY-MM-DD
analyses: N
---
```

正文固定四节：

1. 说明：每次分析自动更新本看板 + 生成简页/深入分析页。
2. 汇总统计（总体分析）：分析次数、平均分、Verdict 分布、最近更新、覆盖目的。
3. 项目列表：每行 = 项目 | 定位一句话 | 总分 | Verdict | 置信度 | 日期 | [[简页]]；简页内含 [[深入分析]] 链接。
4. 模板说明：_模板/ 下两份模板，新项目复制使用。

## 简页（<owner-repo>-简页.md）

frontmatter：type: github-lens-brief；project；url；score；verdict；confidence；date；purpose；tags。

正文五节（每节 ≤5 行）：

1. 一句话定位
2. 核心数据（stars / license / 活跃 / 一句话风险）
3. Verdict 行 + 置信度
4. 关键结论（3–5 条，带证据）
5. 下一步建议 + 链接：`[[<owner-repo>-深入分析|深入分析]]`、`[[GitHub 项目分析看板|看板]]`

## 深入分析（<owner-repo>-深入分析.md）

frontmatter：type: github-lens-deep；project；url；date；purpose；card_version。

正文 = 完整项目卡（references/project_card.md 的七节），并追加：

- 版本 diff（重复分析时）：L1 信号变化 / 锚点变化 / 总分变化 / 对比集变化 / Verdict 是否翻转
- 链接：`[[<owner-repo>-简页|简页]]`、`[[GitHub 项目分析看板|看板]]`

## 更新规则

- 每次分析：先写/更新深入分析 → 简页 → 最后更新看板汇总与列表；
- 同一仓库重复分析：覆盖简页与深入分析内容，diff 保留在深入分析页；
- 看板平均分与 Verdict 分布只统计最新卡片（每项目一行）。
