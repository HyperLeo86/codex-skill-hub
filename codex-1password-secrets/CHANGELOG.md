# CHANGELOG

## 1.0

- 2026-08-03：初始版本。安装包式流程：只读审计（`scripts/audit.sh`）→ G1–G8 差距映射 → 补齐动作 → 验收清单；目标状态与配置块见 `references/target-state.md`。

## 1.1

- 2026-08-03：回灌实测限制——op CLI 稳定版无法创建/读取 SSH Key 类型条目（SSHKEY 字段不支持），G3 明确改为桌面端创建 SSH Key、公钥由用户提供或手工上传。
