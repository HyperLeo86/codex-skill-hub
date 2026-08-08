# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
|（首次使用后按 validation.md 格式追加，升级前全量回归）| | | | |
| 2026-08-08 | wshobson/agents S0 硬指标 | OpenSSF Scorecard API 404（项目未被收录），deps.dev API 未返回数据 | 降级标「待验证」，用 mcpskills 第三方评测补证据 | 已处理 |
| 2026-08-08 | S0 脚本（v0.2 开发） | jq 的 `//` 把布尔 false 当空值，archived=false 输出成 unavailable | 改用 `has()` 判断 + tostring | 已修复 |
| 2026-08-08 | S0 脚本（v0.2 开发） | Scorecard/deps 空响应时字段输出为空串而非 unavailable | 命令替换后加 `${var:-unavailable}` 兜底 | 已修复 |
