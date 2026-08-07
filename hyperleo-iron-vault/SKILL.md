---
name: hyperleo-iron-vault
description: 审计并落地 Codex × 1Password 统一密钥管理；本地 ~/.codex/.env 只作纯 KEY=VALUE 显式缓存，按需 pull/push 同步。当用户说「把 Codex 和 1Password 接起来」「帮我配置 1Password 统一管理密钥」「审计这台电脑的密钥管理现状」「把环境变量和 API Key 迁到 1Password」「把 1Password 里的密钥同步到本地 .env」「把 .env 里新加的 API 上传到 1Password」时使用；不用于：在对话中回显具体密钥值。
---

# 铁金库（Iron Vault）

**版本**：2.0（2026-08-07）

## 概览

1Password 是 API 密钥唯一真相（默认 vault `Private`，可 `OP_CODEX_VAULT` 覆盖）；`~/.codex/.env` 是纯 KEY=VALUE 显式缓存（权限 600，由 `~/.zshrc` source）；`scripts/sync.sh` 负责 pull（下载）与 push（上传）。

## 触发与反触发

- 触发：把 Codex 和 1Password 接起来；帮我配置 1Password 统一管理密钥；审计这台电脑的密钥管理现状；把环境变量和 API Key 迁到 1Password；把 1Password 里的密钥同步到本地 .env；把 .env 里新加的 API 上传到 1Password；Codex 的密钥存在 1Password 里怎么同步；把 .env 里的说明挪到技能里
- 反触发：在对话中回显具体密钥值；管理 1Password 之外的密码库

## 决定权（自由度 low）

- 以 `scripts/audit.sh` 与 `scripts/sync.sh` 为准，顺序、参数、输出格式禁止即兴偏离
- 脚本输出是唯一事实源；密钥值禁止出现在对话、argv、命令历史或日志

## 工作流

1. **审计（只读）**：运行 `scripts/audit.sh`，记录 A1–A6。
2. **差距**：对照 `references/target-state.md` 映射表产出 G1–G9 清单；改动前备份 `~/.codex/config.toml`。
3. **补齐**：只执行差距对应动作；涉及 1Password 的步骤等桌面端授权，不绕过。
4. **同步**：`scripts/sync.sh pull`（1Password → `.env`，只写 KEY=VALUE）；`scripts/sync.sh push`（`.env` → 1Password，条目缺失自动创建 Secure Note；`OP_CODEX_VAULT`/`OP_CODEX_ITEM` 可覆盖）。
5. **验收与报告**：按验收清单逐项 PASS/FAIL；输出摘要、差距、动作与验收表；不回显密钥。

## 验收（来自契约）

- `~/.codex/.env` 只含 KEY=VALUE，无注释与说明
- pull/push 全程不把密钥值写入对话、argv 或日志
- 1Password 不可访问时脚本快速报错并给出 `op signin --account my.1password.com` 指引，不挂起
- 验收表每一项 PASS/FAIL 均可核对

## 失败降级

- op 未登录/桌面端未解锁 → 用 `op vault list` 探活（`op whoami` 在系统认证下会误报），失败则提示 signin
- vault/item 不存在 → push 自动创建 Secure Note；vault 缺失提示 `OP_CODEX_VAULT`
- `.env` 含注释 → pull 重写为纯 KEY=VALUE；push 跳过注释
- 密钥含特殊字符 → 临时文件 + jq 传递，不进 argv/echo
- 条目已有其他字段 → item template 合并，只增改目标字段
- 桌面授权等待 → 停止并提示用户在桌面端批准

## 资源

- `scripts/audit.sh`：只读审计脚本
- `scripts/sync.sh`：pull/push 唯一实现
- `references/target-state.md`：目标状态、差距映射、G1–G9、验收清单
- `references/regressions.md`：回归账本

## Token 预算（220 行 / 2000 token）
