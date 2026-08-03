---
name: codex-1password-secrets
description: 审计任意电脑的 Codex 密钥管理现状，并逐步落地为 1Password 统一管理（安装包式流程：审计 → 差距 → 补齐 → 验收）。当用户说 「把 Codex 和 1Password 接起来」；「帮我配置 1Password 统一管理密钥」；「审计这台电脑的密钥管理现状」；「把环境变量和 API Key 迁到 1Password」；「部署 Codex 的 1Password MCP」；「加固 Codex 的环境变量策略」；「按安装包规范落地密钥管理」 时使用；不用于：在对话中粘贴或回显具体密钥值、管理 1Password 之外的密码库。
---

# codex-1password-secrets

**版本**：1.1（2026-08-03）

## 概览

审计任意电脑的 Codex 密钥管理现状，并逐步落地为 1Password 统一管理（安装包式流程：审计 → 差距 → 补齐 → 验收）

## 触发与反触发

- 触发：把 Codex 和 1Password 接起来；帮我配置 1Password 统一管理密钥；审计这台电脑的密钥管理现状；把环境变量和 API Key 迁到 1Password；部署 Codex 的 1Password MCP；加固 Codex 的环境变量策略；按安装包规范落地密钥管理
- 反触发：在对话中粘贴或回显具体密钥值；管理 1Password 之外的密码库

## 决定权（自由度 low）

- 以脚本/步骤为准，顺序、参数、输出格式禁止即兴偏离
- 脚本输出是唯一事实源，禁止覆盖或重算

## 工作流

1. **审计（只读）**：运行 `scripts/audit.sh`，记录 A1（1Password 桌面端）、A2（op CLI）、A3（SSH）、A4（gh）、A5（Codex）、A6（明文残留）六段输出。
2. **差距**：把审计输出对照 `references/target-state.md` 的「差距映射表」，产出 G1–G8 差距清单；未命中差距的项标 PASS。改动前先备份（`cp ~/.codex/config.toml ~/.codex/config.toml.bak-<日期>`）。
3. **补齐**：按 `references/target-state.md` 的「动作表」只执行差距对应项，已达标项跳过；每个涉及 1Password 的步骤等待桌面端授权，超时则停止并提示，不绕过。
4. **验收**：运行 `references/target-state.md` 的「验收清单」，逐项输出 PASS/FAIL；FAIL 项给出原因与回到的 G 编号。
5. **报告**：输出现状摘要、差距清单、已执行动作与验收表；全程只写变量名与编号，不回显任何密钥值。

## 验收（来自契约）

- 审计步骤只读，不修改任何配置或凭据
- 差距清单每一项都可映射到 G1-G8 动作编号
- 执行过程不把密钥值写入对话、文件或日志
- 验收后明确列出 PASS/FAIL，FAIL 项给出原因与下一步

## 失败降级

- op CLI 未安装或 Homebrew 失败 → 提示手动安装命令，继续执行不依赖 op 的步骤（审计、config 加固）
- 1Password 桌面端授权超时或未解锁 → 停止该步骤并提示用户在桌面端批准，不绕过授权
- config.toml 已存在且有用户改动 → 先备份再合并，禁止覆盖既有配置
- SSH 测试无身份或服务器清单缺失 → 输出待办清单，不猜测服务器地址或创建密钥

## 资源

- `scripts/audit.sh`：只读审计脚本（唯一事实源，先运行）
- `references/target-state.md`：目标状态、差距映射、G1-G8 动作、验收清单（按需加载）
- `references/regressions.md`：回归账本（每次真实使用后回灌）

## Token 预算（契约：180 行 / 2000 token）
