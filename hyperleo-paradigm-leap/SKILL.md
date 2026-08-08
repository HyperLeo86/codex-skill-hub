---
name: hyperleo-paradigm-leap
description: >-
  在解题之前先换坐标系：压缩问题、测量基线、扫描世界、抽象机制、跨域迁移、最小验证、固化进化，寻找数量级提升的解法（降维打击）。当用户说「范式跃迁」「解法跃迁」「降维打击」「十倍改进」「跨域迁移」「深度优化 XX」「有没有更好的解法」「对 XX 做跃迁式升级」时使用。可调用「检索世界 Pro」（hyperleo-world-search-pro）完成扫描层。不用于普通资料查找或单步任务。
---

# 范式跃迁

**版本**：1.3（2026-08-08）

## 定位

在动手解题前，先找到"数量级提升"的路径，而不是优化常数。成功标准：给出「跃迁点在哪里、用什么机制、验证实验是什么」。

## 三条硬规则

1. **检索纪律**：检索完成之前，不允许给出最终方案。
2. **基线纪律**：没有基线对比，不算跃迁，只能叫"换了一种做法"。
3. **取消纪律**：每个候选必须回答「它取消了什么旧工作」；答不上来就淘汰。

## 触发规则

- **完整版（九步）**：以下 5 项满足 3 项——重复发生 / 成本或失败率高 / 规模可能扩大十倍 / 商业价值高 / 依赖大量人工或定制。
- **轻量版（三步）**：意图识别 + 问题压缩 → 快速扫描（复用检索世界 Pro）→ 选成熟方案执行，≤60 分钟。

## 运行模式

- **普通模式**：单轮九步。
- **Loop 模式**：默认 3 轮——第 1 轮发现（压缩→基线→检索世界深扫）；第 2 轮迁移（机制签名 × 跨域工具再检索）；第 3 轮验证与固化（对照实验→复盘→更新案例库→回到第 1 轮）。收敛规则：一轮新增有用候选 < 2 或证伪假设 > 2 提前停止；总轮次 ≤ 3。

## 九步法

| 步骤 | 关键动作 | 工具 | 产物 |
| --- | --- | --- | --- |
| 1 意图识别 + 问题压缩 | 先调用 hyperleo-intent-recognition 输出意图卡；再去行业名词，压缩为「约束下 输入→输出 被什么瓶颈限制」 | 意图识别 skill + TRIZ skill（triz-skill-for-codex） | 意图卡 + 问题定义卡 |
| 2 基线测量 | 五指标 + 成本增长曲线 + 十倍假设 | promptfoo / DeepEval | 基线卡 |
| 3 全域扫描 | 四层：实现 / 原理 / 失败 / 跨域同构 | 调用 `hyperleo-world-search-pro`（Exa+Tavily+渠道矩阵） | 证据清单 |
| 4 解法建图 | 统一矩阵，必答「取消了什么旧工作」 | Heptabase / Obsidian | 方案矩阵 |
| 5 机制抽象 | 五问 + 十操作子打标签 → 机制签名 | Heinrich / TRIZ-Agents / ARIZ-85C | 跃迁模式表 |
| 6 跨域迁移 | 信息结构 / 成本结构 / 失败模式三视角同构 | Analogy-Engine / Artiphron / AskNature | 跨域候选 |
| 7 候选合成 | A 复用 > B 组合 > C 迁移 > D 原创，各带预测提升 | C-K 空间模型 | 候选方案集 |
| 8 最小验证 | 对照基线 + 反向验证 + 十倍检验 | promptfoo + 执行内核 | 验证报告 |
| 9 固化进化 | 更新 Skill + 写入案例库 | SkillWeaver 机制 / skill-creator | 新 Skill + 案例 |

详细工具清单见 [references/tools.md](references/tools.md)；十操作子判别表见 [references/operators.md](references/operators.md)。

## 输出物

```text
01_problem_definition.md
02_baseline.md
03_evidence_map.md
04_solution_matrix.json
05_leap_patterns.md
06_candidate_solutions.md
07_benchmark_plan.md
08_final_recommendation.md
```

轻量版只出 01 + 04 + 08。输出到本次任务工作目录；案例库沉淀到 `~/Documents/leap-cases/`。

## AI 执行纪律

1. 分阶段：未完成检索与建图，禁止合成最终方案。
2. 证据纪律：每个候选必须有真实来源；禁止编造链接；不确定标「待验证」。
3. 反例纪律：每个候选必须给出「什么条件下会失效」。
4. 不贪全：触发条件不满足就走轻量版。
5. 机制优先：评价以「取消了什么旧工作、改变了什么成本关系」为核心，不以技术新颖性为核心。
6. 回归纪律：每次真实使用后把失败记入 `references/regressions.md`；升级前全量回归，存在「未修复」不得升级。

详细工具清单见 [references/tools.md](references/tools.md)；十操作子判别表见 [references/operators.md](references/operators.md)；回归账本见 [references/regressions.md](references/regressions.md)。
