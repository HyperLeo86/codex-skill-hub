# CHANGELOG

## 2.0（2026-08-07）

- 重命名：codex-1password-secrets → hyperleo-iron-vault（HyperLeo 命名规范，主题设计保留，破坏性变更）
- 版本 1.3 → 2.0

## 1.3（2026-08-07）HyperLeo 重命名

- codex-1password-secrets → hyperleo-iron-vault（HyperLeo 命名规范）

## 1.0

- 2026-08-03：初始版本。安装包式流程：只读审计（`scripts/audit.sh`）→ G1–G8 差距映射 → 补齐动作 → 验收清单；目标状态与配置块见 `references/target-state.md`。

## 1.1

- 2026-08-03：回灌实测限制——op CLI 稳定版无法创建/读取 SSH Key 类型条目（SSHKEY 字段不支持），G3 明确改为桌面端创建 SSH Key、公钥由用户提供或手工上传。

## 1.2

- 2026-08-07：新增上传/下载能力——`scripts/sync.sh pull|push` 作为唯一实现；本地缓存模型改为 `~/.codex/.env` 纯 KEY=VALUE（说明移入技能文档）；provider 一律 `env_key`，禁止明文 token/URL 内嵌 key；op 未登录快速失败不挂起；新增 G9 动作与验收 11–13；回灌首次接入、.env 注释、op 挂起、`max` 配置解析四条回归记录。

## 1.3

- 2026-08-07：实机验证与修复——`op whoami` 在系统认证下误报 not signed in，探活改为 `op vault list`（timeout 兜底）；默认 vault 从 `Personal` 改为本机实际使用的 `Private`（`OP_CODEX_VAULT` 仍可覆盖）；`op://vault/title` 解析失败导致重复创建，存在性改为 list+精确匹配、多同名报错；更新字段按 id/label 替换后再追加，避免 non-unique name；完成 `Private/Codex API` 条目创建、更新与密钥写入验收。
