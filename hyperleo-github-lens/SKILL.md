---
name: hyperleo-github-lens
description: 把任意 GitHub URL 变成一张可复现、可校准、可累积的项目分析卡，并同步进 Obsidian 看板（汇总 + 简页 + 深入分析）。当用户说 「分析一下这个 GitHub 项目」；「帮我看看这个仓库值不值得学/用」；「把这个 GitHub 链接拆解一下，告诉我它怎么工作的」；「对比一下这两个 GitHub 项目」；「给这个开源项目打个分」；「研究一下这个 repo，输出一份项目分析卡」；「这个项目有没有价值，值得深入学习吗」；「重新分析一下这个项目，看看和上次有什么不同」 时使用；不用于：发布/同步技能到 GitHub、只修 bug 或重构某个仓库的代码、做市场调研或竞品全景报告。
---

# hyperleo-github-lens

**版本**：0.3.0（2026-08-08）

## 概览

把任意 GitHub URL 变成一张可复现、可校准、可累积的项目分析卡，并同步进 Obsidian 看板（汇总 + 简页 + 深入分析）

## 触发与反触发

- 触发：分析一下这个 GitHub 项目；帮我看看这个仓库值不值得学/用；把这个 GitHub 链接拆解一下，告诉我它怎么工作的；对比一下这两个 GitHub 项目；给这个开源项目打个分；研究一下这个 repo，输出一份项目分析卡；这个项目有没有价值，值得深入学习吗；重新分析一下这个项目，看看和上次有什么不同
- 反触发：发布/同步技能到 GitHub；只修 bug 或重构某个仓库的代码；做市场调研或竞品全景报告

## 决定权（自由度 medium）

- 按伪代码/模板执行，参数可依上下文调整
- 输出格式遵循模板，内容允许合理变化
- L1 脚本输出是客观信号唯一事实源，禁止覆盖或重算；L2 语义判断允许合理变化
- Obsidian 三件套结构以 references/obsidian_layout.md 为准，页面内容允许合理变化

## 工作流

输入归一化：接受 GitHub URL、`owner/repo` 或本地路径；先记录目的标签（学习/采用/选型/对标），缺省「学习」，输出时提示可换权重。

### S0 L1 确定性信号层（脚本化）

1. 运行 `scripts/repo_meta.sh owner/repo`，一次产出统一 JSON：GitHub 元数据（stars/forks/license/archived/pushed_at/open_issues/topics/contributors）、OpenSSF Scorecard、deps.dev、star health（Star/Fork、Star/Issue、Fork 率）、最近提交日期。
2. 红旗判定：archived / 停更 >12 个月 / license 缺失 / 刷星证据（Star/Fork>20、Star/Issue>200 且活跃度不符）。
3. 输出：L1 信号表 + 红旗清单 + 判定（过 / 条件过 / 不过）。

API 失败字段标 `unavailable`（如 Scorecard 未收录），不阻塞，语义层降级标注「待验证」。

### S1 价值理解（Why）

回答 9 问：定位 / 受众 / 时机 / 采用信号 / 社区真实度 / 商业模式 / 学习价值 / 采用价值 / 风险。客观数字一律引用 L1 表；README 不算独立证据，至少找 1 个第三方来源；不确定标「待验证」。

### S2 逻辑拆解（How）

1. clone 到临时目录（大仓 `--depth 1`）。
2. 读目录职责 + 技术栈（package.json / pyproject.toml / go.mod / requirements.txt）。
3. 找入口与核心模块，画数据流，记关键机制（Why > What）。
4. 提炼设计取舍与可借鉴模式。

深度按目的自适应：学习 → Deep 倾向；采用/选型 → Standard + License/集成/文档重点；对标 → 架构与定位重点。超时降档 Quick（核心模块覆盖 ≥30%），深读标为下一步。

### S3 锚点校准评分（Score）

1. 读 references/anchors.md，选 1–2 个同形态锚点（如工具库、技能生态、官方仓库）。
2. L1 信号自动映射客观维度基础分；L2 语义维度相对锚点解释 ±分，每个 L2 得分必须写「相对锚点 X 高/低多少，因为……」。
3. 按目的标签选权重表（references/scoring_rules.md 四套：学习/采用/选型/对标）。
4. 风险扣分 + 一票否决 + 置信度。

每次必出：

```
Verdict: <学它|用它|对标它|放弃|观察> — <项目名> — <核心证据，禁止形容词>
置信度: HIGH|MEDIUM|LOW
```

置信度 MEDIUM 以下不给「用它」。

### S4 同类对比（Compare）

1. 先查知识库历史卡片（默认 outputs/ 或 ~/Documents/project-cards/），复用已有对比集。
2. 增量补：README Alternatives → GitHub Topics（stars:>100）→ `项目名 alternative/vs` 反向搜 → 社区讨论（HN/Reddit/V2EX）。
3. 输出对比表（定位 / 架构 / 许可 / 活跃 / 上手 / 适用场景 / 学习点）+ 一句话定位差异；标注哪些来自历史库、哪些是本次新增。

### S5 交付与归档（Obsidian 三件套）

1. 按 references/project_card.md 产出完整分析卡（含版本 diff）。
2. 定位 Vault：`scripts/obsidian_locate.sh`（优先级：环境变量 OBSIDIAN_VAULT → obsidian.json 中 open:true 的仓库 → 第一个仓库）。
3. 按 references/obsidian_layout.md 写入/更新三件套：
   - 看板汇总：更新统计与项目列表（含本项目的简页链接）；
   - 简页：一句话定位、核心数据、Verdict、关键结论、指向深入分析的链接；
   - 深入分析：完整分析卡内容，指向简页与看板。
4. 若该仓库已有历史卡片：diff 写入深入分析页；否则标注「首次分析，无 diff」。
5. Vault 定位失败 → 三件套写入 `outputs/obsidian-export/` 并在报告中提示配置 OBSIDIAN_VAULT。
6. 本次失败（如有）按一行式追加 references/regressions.md。

## 验收（来自契约）

- 每次输出必含 Verdict 行（学它/用它/对标它/放弃/观察 + 证据）与置信度（HIGH/MEDIUM/LOW）
- 评分每一项都有证据来源或显式标注「待验证」，禁止无证据打分
- 评分必须拆分为 L1 确定性信号与 L2 语义判断，且每个 L2 维度相对 references/anchors.md 的锚点解释
- 必须产出至少 1 张同类对比表（≥2 个项目，含定位差异）
- S0 红旗命中（archived/停更>12 个月/无 License/刷星证据）必须显式写进结论
- 重复分析同一仓库时，必须输出与历史卡片的版本差异（diff）；首次分析标注「首次，无 diff」
- 每次分析必须产出/更新 Obsidian 三件套：看板汇总、简页、深入分析页（找不到 Vault 时降级到 outputs 并在报告中说明）

## 失败降级

- 链接无效/仓库不存在/私有仓库 → 停止分析并报告错误类型，不编造元数据
- GitHub API 限流或元数据缺失 → L1 脚本输出 unavailable，用仓库页面可见信息降级并标「待验证」
- 仓库超大导致分析超时 → 降档 Quick：只做概览+目录职责，深读标为下一步
- License 缺失或 AGPL/GPL/BSL → 显式写出合规后果并计入一票否决/条件通过
- 找不到同类项目 → 降级为生态位判断：说明无直接同类+最近邻替代，不编造对比
- 目的标签缺失 → 默认「学习」权重，输出中提示可换权重
- 知识库无历史卡片 → 标注「首次分析」，跳过 diff，对比集走搜索
- Obsidian Vault 未找到 → scripts/obsidian_locate.sh 定位失败时，把三件套写入 outputs/obsidian-export/ 并在报告中提示配置 OBSIDIAN_VAULT

## 资源

- scripts/repo_meta.sh：L1 确定性信号抓取（GitHub API + Scorecard + deps.dev + star health）
- scripts/obsidian_locate.sh：定位 Obsidian Vault 路径
- references/anchors.md：校准锚点（评分参照系）
- references/scoring_rules.md：L1/L2 拆分、四套目的权重、一票否决、置信度
- references/project_card.md：项目卡输出模板（含版本 diff 节）
- references/obsidian_layout.md：Obsidian 看板三件套结构与模板
- references/regressions.md：回归账本（每次真实使用后追加失败行）

## Token 预算（契约：280 行 / 2400 token）
