# Changelog

格式：SemVer + 日期；变更记录只放本文件，不进 skill 文件夹。

## 2026-08-03 · 初始入库

### fan-shi-yue-qian 1.0.0

- 首次纳入版本管理（此前无版本标记），SKILL.md 增加版本行。

### jian-suo-shi-jie 1.3.0

- 首次纳入版本管理；文档版本号由 v1.3 规范化为 v1.3.0，SKILL.md 增加版本行。

### jian-suo-shi-jie-pro 1.4.0

- 首次纳入版本管理；文档版本号由 v1.4 规范化为 v1.4.0，SKILL.md 增加版本行。
- 相对 v1.3.0 的五项升级：查询变体扩展、多路合并重排、历史库回灌、检索日志、验证反馈补搜。

### skill-forge-1-1 1.1.0

- 首次纳入版本管理；版本号由 v1.1 规范化为 v1.1.0，SKILL.md 增加版本行。
- 定位：官方 Skill Creator 常规升级版（意图捕获卡、token 硬预算、验证门、TDD 式前向测试）。

### skill-forge-1-2 1.2.0（恢复）

- 该版本曾被另一会话原地升级为 1.3 且未保留副本；本条目从 2026-08-03 skill-creator 会话 outputs 备份完整恢复（与 2026-08-02 备份内容一致）。
- v1.2.0 相对 v1.1.0：契约闭环五步（压缩 → 生成 → 验证 → 回灌 → 固化）、一页契约模板、token 预算表、A/B 前向测试协议、失败模式账本、build_skill.py 规格驱动生成。

### skill-forge-1-3 1.3.0

- v1.2.0 → v1.3.0 六项升级：
  1. 契约校验化：触发句下限统一为 ≥6，check 新增 spec 必填字段校验（triggers / anti_triggers / acceptance / failure_modes / token_budget）
  2. 账本种子：build_skill.py 自动生成 references/regressions.md，check 校验存在性
  3. 决定权条款：生成器按 freedom 输出「该锁死/该留白」条款，Block 三原则固化到产物
  4. description 升级：第三人称能力描述 + 触发句直接罗列 + 反触发
  5. 版本纪律：SKILL.md 头部一行版本 + 日期；完整变更记录放 skill 文件夹之外
  6. 检查强化：name=父目录同名、folded description 解析、references 一层深、脚本可执行位、账本存在性

## 待办（后续轮次）

- 发布门自动化：tag 推送后自动生成 GitHub Release 与版本摘要
- skill-forge 系列目录合并方案评估（单一 `skill-forge` 目录 + tag 管理）
- 公开分享前的 LICENSE 选择与 marketplace 清单
