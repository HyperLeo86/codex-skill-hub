# 工具矩阵

九步法每步可接入的现成工具（2026-08 扫描结果，均需双源验证后使用）。

| 步骤 | 工具 | 链接 | 用途 |
| --- | --- | --- | --- |
| 1 问题压缩 | triz-skill-for-codex | https://github.com/sauah666/triz-skill-for-codex | 矛盾识别与问题解析 |
| 1 问题压缩 | triz-engineering-solver | https://github.com/Antropocosmist/triz-engineering-solver | 39×39 矩阵 + 40 原理 + Su-Field + ARIZ-85C |
| 2/8 基线验证 | promptfoo | https://www.promptfoo.dev/docs/guides/ | LLM/Agent 评测、回归、LLM-as-judge |
| 2/8 基线验证 | DeepEval / Inspect AI | https://futureagi.com/blog/best-open-source-eval-frameworks-2026/ | Agent 评估框架 |
| 3 全域扫描 | 检索世界（world-search） | /Users/leo/.codex/skills/world-search | Exa + Tavily + 渠道矩阵 + 深度扫描 |
| 4 解法建图 | Heptabase / Obsidian / Causal Map | https://garden.causalmap.app/ | 候选矩阵与因果可视化 |
| 5 机制抽象 | Heinrich - The Inventing Machine | https://github.com/NickScherbakov/Heinrich-The-Inventing-Machine | 开源 TRIZ AI 引擎（矛盾矩阵 + LLM 推理流） |
| 5 机制抽象 | TRIZ-Agents | https://arxiv.org/abs/2506.18783 | 多智能体 TRIZ（ICAART 2025） |
| 6 跨域迁移 | Analogy-Engine | https://github.com/HELALI-Amin-24005915/Analogy-Engine | 多智能体跨域类比引擎（三层本体） |
| 6 跨域迁移 | Artiphron（专利类比检索） | https://www.cambridge.org/core/journals/ai-edam/article/knowledge-graphassisted-designbyanalogy-promoting-product-innovation-through-structured-analogical-knowledge-retrieval/9A6F1AFD04B956722EAFB62DEDC9ECFD | 按功能检索专利类比 |
| 6 跨域迁移 | morphism-mapper | https://github.com/pinren/morphism-mapper | 范畴论跨域问题映射 |
| 6 跨域迁移 | AskNature / FindStructure | https://asknature.org/ | 按功能搜索生物机制库 |
| 7 候选合成 | C-K 理论（LLM 化） | https://www.ck-theory.org/c-k-theory/ | 概念空间 × 知识空间算子演化 |
| 9 固化进化 | SkillWeaver（OSU） | https://github.com/OSU-NLP-Group/SkillWeaver | Agent 技能自发现/打磨/复用 |
| 9 固化进化 | skill-creator | /Users/leo/.codex/skills/.system/skill-creator | 创建/更新 Skill 的官方规范 |

## 使用规则

- 工具是手段，九步是流程；工具找不到时用方法代替，不要卡住。
- 每个工具首次使用前做最小试跑（≤30 分钟），失败则降级为「只借鉴」。
- 商业工具（如 Goldfire）默认不引入，除非用户明确要求。
