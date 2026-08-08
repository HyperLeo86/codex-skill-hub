---
name: hyperleo-hub-sync
description: 把私有技能仓库 codex-skill-hub 的最新版本拉取到本机并更新 ~/.codex/skills：git 拉取 → 逐技能比对 → 备份旧版 → 覆盖安装 → 报告差异。当用户说 「更新我的技能库」；「把 codex-skill-hub 的最新版本更新到本地」；「同步技能库到本地」；「把 GitHub 上的技能更新到本地」；「更新本地 skills」；「拉取技能库的最新版本」；「我的技能是不是有新版本，更新一下」 时使用；不用于：把本地技能发布/推送到 GitHub（走 hyperleo-skill-publisher）、创建或升级技能内容本身（走 hyperleo-skill-forge）、分析技能质量（走 hyperleo-skill-analyst）。
---

# hyperleo-hub-sync

**版本**：0.2（2026-08-07）

## 概览

把私有技能仓库 codex-skill-hub 的最新版本拉取到本机并更新 ~/.codex/skills：git 拉取 → 逐技能比对 → 备份旧版 → 覆盖安装 → 报告差异

## 依赖

- bash 3.2+、git、网络
- 私有仓库凭据：`gh auth login` 或 SSH key（脚本用 HTTPS + 系统凭据，不做交互式登录）

## 触发与反触发

- 触发：更新我的技能库；把 codex-skill-hub 的最新版本更新到本地；同步技能库到本地；把 GitHub 上的技能更新到本地；更新本地 skills；拉取技能库的最新版本；我的技能是不是有新版本，更新一下
- 反触发：把本地技能发布/推送到 GitHub（走 hyperleo-skill-publisher）；创建或升级技能内容本身（走 hyperleo-skill-forge）；分析技能质量（走 hyperleo-skill-analyst）

## 决定权（自由度 low）

- 以脚本/步骤为准，顺序、参数、输出格式禁止即兴偏离
- 脚本输出是唯一事实源，禁止覆盖或重算

## 工作流

1. **参数确认**：使用默认值（仓库 `HyperLeo86/codex-skill-hub`、分支 `main`、mirror `~/.codex/skill-hub`、目标 `~/.codex/skills`、备份 `~/.codex/skill-hub-backups`）；用户显式指定时以环境变量 `HUB_REPO` / `HUB_BRANCH` / `HUB_MIRROR_DIR` / `CODEX_SKILLS_DIR` / `HUB_BACKUP_DIR` 覆盖。
2. **预览（可选）**：先跑 `DRY_RUN=1 bash scripts/hub_sync.sh`，只展示将要新增 / 更新 / 备份的技能，不写任何文件。
3. **执行**：跑 `bash scripts/hub_sync.sh`。脚本负责 clone/pull mirror、逐技能比对、备份旧版、覆盖安装；脚本输出是唯一事实源，禁止手工重算或跳过步骤。
4. **报告**：把脚本输出整理成摘要：新增 / 更新（含备份路径）/ 未变 / 本地独有；提示用户「新版本在下一次对话生效」。

## 使用

```bash
# 直接同步
bash scripts/hub_sync.sh

# 先预览再同步
DRY_RUN=1 bash scripts/hub_sync.sh
```

脚本会跳过仓库里不含 `SKILL.md` 的目录，不删除目标目录中「仓库里不存在」的技能，只把它们列成「本地独有」供用户决定。
`DRY_RUN=1` 需要本地已有 mirror（先真实同步过一次）。

## 验收（来自契约）

- 本地 mirror 与远端 main 一致（git fetch + reset 成功）
- 仓库内每个含 SKILL.md 的一层目录在目标目录都有同名最新副本
- 被覆盖的目标目录先整体备份到 backup 目录，摘要列出备份路径
- DRY_RUN=1 时只预览不写任何目标文件

## 失败降级

- 私有仓库无凭据 → 报错并提示 gh auth login 或配置 SSH，不猜测凭据
- mirror 有本地改动导致 pull 冲突 → mirror 视为只读缓存，用 fetch + reset --hard 对齐远端；失败则停止且不动目标目录
- 目标目录有本地改动 → 先整体备份再覆盖，绝不静默删除；摘要给出备份路径
- 网络不可用 → 明确报错，保留现有本地副本不动作
- 仓库内出现非技能目录或损坏的 SKILL.md → 跳过并列出，不做猜测性处理

## 资源

- scripts/hub_sync.sh：确定性同步逻辑，直接运行
- scripts/self_test.sh：本地 fixture 回归（不依赖网络/私有仓库）
- references/：按需加载的细节（含回归账本 regressions.md）

## 维护

- 修改脚本或 SKILL.md 后：跑 `bash scripts/self_test.sh` 做回归
- 发布前用 skill-forge 的 `check_skill.py` 校验结构/token
- 大模型升级后先重跑 `self_test.sh` 与 `references/regressions.md` 全部场景，再删除为旧模型打的补丁

## Token 预算（契约：200 行 / 1800 token）
