---
name: hyperleo-skill-lens
description: 把任意 Agent Skill（GitHub 链接 / 本地 SKILL.md / 仅名称）变成一张可收藏的「说明图片」（PNG 海报）：一句话定位 + 比喻逻辑 + 好处场景 + 模块可替换性。当用户说 「帮我看看这个 skill 是干什么的」；「把 xxx 这个 skill 画成图给我看」；「把这个 skill 做成一张说明海报」；「这个 GitHub 链接里的 skill 讲的是什么」；「帮我理解一下这个技能的逻辑」；「这个 skill 有几个模块，能替换吗」；「给我一张这个 skill 的身份卡」；「把本地这个 skill 文档做成可视化网页」；「帮我查一下 xxx skill 然后解释给我听」 时使用；不用于：深度体检/优化 skill（走 hyperleo-skill-analyst）、创建/升级一个新技能（走 hyperleo-skill-forge）、发布技能到 GitHub（走 hyperleo-skill-publisher）、检索世界上有没有现成方案（走 hyperleo-world-search-pro）。
---

# hyperleo-skill-lens

**版本**：0.2（2026-08-07，待完善）
**状态**：待完善——核心「一张图」闭环已验证；高级渲染层、AI 插画版面、卡片归档未接

## 概览

把任意 Agent Skill 变成一张可收藏的说明图片（PNG 海报）：一句话定位 + 比喻逻辑 + 好处场景 + 模块可替换性。输出是图片，不是结构图/流程图。

## 触发与反触发

- 触发：帮我看看这个 skill 是干什么的；把 xxx 这个 skill 画成图给我看；把这个 skill 做成一张说明海报；这个 GitHub 链接里的 skill 讲的是什么；帮我理解一下这个技能的逻辑；这个 skill 有几个模块，能替换吗；给我一张这个 skill 的身份卡；把本地这个 skill 文档做成可视化网页；帮我查一下 xxx skill 然后解释给我听
- 反触发：深度体检/优化 skill（走 hyperleo-skill-analyst）；创建/升级一个新技能（走 hyperleo-skill-forge）；发布技能到 GitHub（走 hyperleo-skill-publisher）；检索世界上有没有现成方案（走 hyperleo-world-search-pro）

## 决定权（自由度 medium）

- 按伪代码/模板执行，参数可依上下文调整
- 输出格式遵循模板，内容允许合理变化

## 工作流（输入 → 提炼 → 卡片化 → 渲染 → 自检）

0. **输入解析**
   - GitHub 链接：`git clone --depth 1 <url> <work>/<repo>`（私有仓库提示用户授权，不猜凭据）
   - 本地路径：直接解析；路径不存在 → 停止并询问
   - 仅名称：先 `rg --files ~/.codex/skills ~/.agents/skills ~/.claude/skills 2>/dev/null | rg '/SKILL\.md$'` 查本地并让用户确认候选；需要深挖时再走 hyperleo-world-search-pro；仍无 → 走失败降级 1
1. **取证**：优先运行 `hyperleo-skill-analyst/scripts/analyze_skill.py <dir>` 收集静态事实（行数/token/版本/引用完整性）；读 SKILL.md 的 frontmatter、工作流、失败降级、资源清单、目录树；超 10k token 走渐进式披露
2. **提炼（不优化，不画结构图）**：识别一句话定位 / 好处 / 适用场景 / 注意事项；给 1–2 个比喻（像什么/哪像/哪不像）；提炼 3–5 个关键要点（含模块可替换性判定）；产出「卡片文案」而不是节点图
3. **卡片化**：按 references/poster-template.md 把文案排成 1200×1600 海报（标题 / 副标题 / 比喻卡 / 要点区 / 模块标签 / 证据脚注）；禁止 Mermaid、SVG、流程图、架构图
4. **渲染**：优先 `scripts/render_poster.sh <poster.html> <out.png>`（本地 Chrome → PNG）；若已安装 card-skill 或 infocard-skills 可交给其渲染；可选 hyperleo-image-gen-router 生成比喻插画作背景；交付 PNG 绝对路径 + 海报 HTML 源
5. **自检**：对照 references/analysis-checklist.md 逐条验收；不达标最多返工 2 轮，仍不达标输出「海报 HTML + 未渲染标注」

## 组合关系（怎么包装现有技能）

- 分析层：复用 hyperleo-skill-analyst（取证脚本）
- 查找层：仅名称输入默认本地 rg + 用户确认；需要深挖时再走 hyperleo-world-search-pro
- 渲染层：默认本地 Chrome HTML→PNG；可选现成卡片技能（card-skill / infocard-skills）；可选 AI 插画（hyperleo-image-gen-router）
- 边界：本技能只做「理解与呈现」，优化走 hyperleo-skill-analyst，创建走 hyperleo-skill-forge，发布走 hyperleo-skill-publisher

## 验收（来自契约）

- 输出为一张 PNG 说明海报（含 HTML 源），不是结构图/流程图
- 海报含：标题 / 一句话定位 / 比喻（像什么+哪像+哪不像）/ 3–5 个要点（好处、场景、模块可替换性）
- 比喻三要素齐备，禁止只给一个比喻词
- 模块可替换判定三档（可替换/难替换/不可替换）+ 理由
- 仅名称输入时先本地后网络；查不到必须明确说「未找到」并给相近本地项，禁止编造
- PNG 可由本地 Chrome 从 HTML 源复现渲染；AI 插画失败不阻塞出图

## 失败降级

- 输入仅一个名称且本地/网络都查不到 → 停止并列出本地已安装的相近技能，明确标注「未找到」，不编造内容
- GitHub 链接不是 skill 而是普通仓库 → 先识别仓库形态：含 SKILL.md/plugins/skills 目录按 skill 处理，否则输出仓库概览并说明它不是标准 skill
- 目标 skill 文档缺失或权限不足 → 基于现有文件分析，报告里标注「未覆盖资源」
- 目标 SKILL.md 极长（>10k token） → 渐进式披露：先读 frontmatter/标题/工作流/资源清单，再按需读 references，禁止一次全量读入
- 目标 skill 的脚本/引用资源无法运行 → 静态分析 + 输出标注「未实证」，不编造运行结果
- Chrome 不可用或截图失败 → 交付海报 HTML 源并标注「未渲染」，不阻塞
- AI 插画无 Key / 失败 → 纯 CSS 海报照常出图，不阻塞
- scripts/render_poster.sh 无法运行 → 手工执行等价的 Chrome headless 命令

## 资源

- scripts/render_poster.sh：本地 Chrome HTML→PNG 渲染（直接运行）
- references/poster-template.md：1200×1600 海报模板与样式规范（渲染前必读）
- references/analysis-checklist.md：海报验收清单与证据规则（自检必读）
- references/regressions.md：回归账本
- 复用不复制：hyperleo-skill-analyst 取证、hyperleo-world-search-pro 可选查找、card-skill / infocard-skills 可选渲染、hyperleo-image-gen-router 可选插画

## Token 预算（契约：220 行 / 2000 token）
