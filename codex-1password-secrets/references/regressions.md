# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-03 | 落地 G3（SSH 密钥入库） | op CLI 2.38.1 无法创建/读取 SSH Key 条目（unknown field types / invalid PEM），SSH 通道一度卡住 | G3 改为桌面端创建 SSH Key + 公钥由用户提供/上传；限制写入 target-state 已知限制 | 已修复 |
