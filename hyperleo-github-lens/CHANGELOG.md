# CHANGELOG · hyperleo-github-lens

## 0.3.0（2026-08-08）

- 新增 Obsidian 三件套集成：看板汇总、简页、深入分析页，每次分析必须产出/更新
- 新增 scripts/obsidian_locate.sh：自动定位 Vault（OBSIDIAN_VAULT → open 仓库 → 第一个仓库）
- 新增 references/obsidian_layout.md：三件套目录结构、frontmatter 与更新规则
- S5 改为「交付与归档（Obsidian 三件套）」；Vault 定位失败降级到 outputs/obsidian-export/

## 0.2.0（2026-08-08）

- 新增 L1 确定性信号层：scripts/repo_meta.sh 统一抓取 GitHub API / OpenSSF Scorecard / deps.dev / star health
- 新增锚点校准评分：references/anchors.md，L2 语义维度必须相对锚点解释
- 新增目的自适应权重：学习 / 采用 / 选型 / 对标 四套权重表
- 新增知识库版本 diff：重复分析输出 L1/评分/对比集/结论差异
- 新增触发句「重新分析一下这个项目，看看和上次有什么不同」
- 失败降级补充：目的标签缺失、知识库无历史卡片

## 0.1.0（2026-08-08）

- 初版：五段工作流（预检快照 → 价值理解 → 逻辑拆解 → 100 分制评分 → 同类对比 → 归档）
- references：project_card.md、scoring_rules.md、regressions.md
