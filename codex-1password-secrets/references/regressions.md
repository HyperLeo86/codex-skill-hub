# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-03 | 落地 G3（SSH 密钥入库） | op CLI 2.38.1 无法创建/读取 SSH Key 条目（unknown field types / invalid PEM），SSH 通道一度卡住 | G3 改为桌面端创建 SSH Key + 公钥由用户提供/上传；限制写入 target-state 已知限制 | 已修复 |
| 2026-08-07 | 首次接入 | 实际并未接入 1Password：op 未登录、无插件配置，密钥明文散落在 .zshrc/config.toml，Codex 靠 shell 快照隐式注入 | 落地本地 .env 显式缓存 + provider 一律 env_key + sync.sh pull/push；require_op 快速失败 | 已修复 |
| 2026-08-07 | .env 初始版本 | .env 写入大段中文说明，违背“纯键值缓存”定位 | 说明移入 SKILL.md 与 target-state.md；.env 只保留 KEY=VALUE | 已修复 |
| 2026-08-07 | op 未登录执行 vault/item 命令 | 命令静默挂起，无任何提示 | sync.sh 先 op whoami 快速失败并给出 signin 指引 | 已修复 |
| 2026-08-07 | CLI 加载配置 | config.toml/models.json 含 `max`，CLI 0.131 解析失败，codex login status 不可用 | 统一改为 `xhigh`，codex doctor 验证通过 | 已修复 |
| 2026-08-07 | 实机写入 Codex API | 系统认证下 `op whoami` 误报 not signed in，require_op 拦下所有操作；桌面授权响应可慢至 ~45s，10s 探活误杀 | 改用 `op vault list` 探活（timeout 60s 兜底） | 已修复 |
| 2026-08-07 | 实机写入 Codex API | 默认 vault `Personal` 与实际 `Private` 不符，首次 push 会指向错误位置 | 默认改为 `Private`，`OP_CODEX_VAULT` 可覆盖 | 已修复 |
| 2026-08-07 | 实机更新 Codex API | `op://vault/title` 按标题解析失败，导致重复创建同名条目；更新时字段直接 append 触发 non-unique name 校验错误 | 存在性改为 list+精确匹配；字段按 id/label 替换后再追加 | 已修复 |
