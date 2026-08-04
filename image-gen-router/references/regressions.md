# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-04 | 首次接入 DashScope 生图 | compatible-mode `/v1/images/generations` 返回 404，误以为 Key 无效 | 改用原生 multimodal-generation / image-generation 端点，qwen-image-2.0-pro、z-image-turbo、wan2.7-image-pro 验证成功 | 已修复 |
| 2026-08-04 | 首次接入 ARK Seedream | `doubao-seedream-5-0-260128` 返回空结果（n=0） | 改用 `doubao-seedream-5-0-pro-260628`，成功出图 | 已修复 |
