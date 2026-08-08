# codex-skill-hub

个人 Codex 技能集合与版本管理仓库（私有）。每个技能只保留一个最新版本目录，版本历史记录在各自文件夹的 CHANGELOG.md。

## 技能清单

| 技能 | 版本 | 说明 |
| --- | --- | --- |
| hyperleo-ash-verdict | 1.0 | 任务或过程失败后，重放意图与过程，只输出事实、1-2 条技术性错误/缺失、0-1 条人文性错误/概念，并写入错误日志 |
| hyperleo-github-lens | 0.3.0 | 把任意 GitHub URL 变成一张可复现、可校准、可累积的项目分析卡，并同步进 Obsidian 看板（汇总 + 简页 + 深入分析） |
| hyperleo-hub-sync | 0.2 | 把私有技能仓库 codex-skill-hub 的最新版本拉取到本机并更新 ~/.codex/skills：git 拉取 → 逐技能比对 → 备份旧版 → 覆盖安装 → 报告差异 |
| hyperleo-image-gen-router | 1.1 | 统一路由并调用用户已开通的生图 API（阿里通义万相 DashScope、火山方舟 ARK），按可用 Key 与任务类型自动选择模型，未来新增提供方只需扩展注册表 |
| hyperleo-intent-recognition | 0.1.0 | 任务/技能开工前的意图识别与澄清：识别真实意图、澄清模糊目标、输出意图卡（What/For whom/Decision/Success signal/Relationship），确… |
| hyperleo-iron-vault | 1.4 | 审计并落地 Codex × 1Password 统一密钥管理；本地 ~/.codex/.env 只作纯 KEY=VALUE 显式缓存，按需 pull/push 同步 |
| hyperleo-paradigm-leap | 1.3 | 在解题之前先换坐标系：压缩问题、测量基线、扫描世界、抽象机制、跨域迁移、最小验证、固化进化，寻找数量级提升的解法（降维打击） |
| hyperleo-persona-scout | 0.2.0 | 按关系身份输出带证据分级的关系情报：消费意图卡 → 事实层一次检索 → 关系透镜 → 行动建议 |
| hyperleo-prd-writer | 1.1 | 示例驱动的可执行 PRD（产品需求文档）撰写与审核技能：三视角访谈 → 概念版对齐 → 落地版（每条规则配例子、AC 产出 GWT）→ DoR 100 分闸门 → 纵横审核 → 交… |
| hyperleo-skill-analyst | 1.2 | 对现有 Skill 做四维体检（逻辑/可用性/可修改性/可进化），输出带证据的问题清单与精准优化方案，也可输出「身份卡」概览 |
| hyperleo-skill-audit | 0.1.0 | 审视一个 Skill 的合理性：纯粹性、功能解耦、独立意图与生态位，输出裁决卡与「独立/合并/拆分/重构」建议 |
| hyperleo-skill-forge | 1.5 | 用「契约驱动 + 可测试 + 自进化」创建或升级 Agent 技能（Skill），统一版 v1.5：契约校验化、HyperLeo 命名规范、账本种子与发布门 |
| hyperleo-skill-lens | 0.2 | 把任意 Agent Skill（GitHub 链接 / 本地 SKILL.md / 仅名称）变成一张可收藏的「说明图片」（PNG 海报）：一句话定位 + 比喻逻辑 + 好处场景 +… |
| hyperleo-skill-publisher | 1.4 | 按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub |
| hyperleo-small-council | 0.2 | 把高风险、多步骤、多 agent 的交付任务变成「分权 + 证据 + 状态机 + 人工门」的治理系统：实现、审查、发布、记账角色分离，流程可恢复，失败可沉淀 |
| hyperleo-world-search-pro | 1.2 | 动手前的方案侦察 + 决策 + 归档完整流水线：多引擎检索、六层选型、业务价值与许可硬检查、谱系解释、Verdict 行与置信度、报告归档 |
| medlit-search | 0.1 | 医药/生命科学文献检索与交叉验证（NCBI E-utilities/PubMed + Europe PMC REST API） |

## 版本管理规则

- 每类技能只保留一个最新版本目录（幂等），同一项目只有一个文件夹
- 版本号按 1.1、1.2 式排序；历史变更记录在对应文件夹的 `CHANGELOG.md`
- 每个技能用 tag `技能名@vX.Y` 标记当前版本，例如 `skill-forge@v1.3`
- 旧版本不另建目录，由 git 提交历史保留
- 初始入库日期：2026-08-03

## 本地安装

把对应技能目录复制到 `~/.codex/skills/` 下即可：

```bash
cp -R skill-forge ~/.codex/skills/
```

## 说明

- 检索类脚本所需的 API key（Exa / Tavily）不随仓库分发，从环境变量或 `~/.config/world-search/*.env` 读取（兼容旧路径 `~/.config/jian-suo-shi-jie/`）
- 当前为私有仓库；如后续要公开，需要先补充 LICENSE
