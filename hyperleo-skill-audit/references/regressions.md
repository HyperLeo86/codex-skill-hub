# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-08 | v0.1.0 审计裁决 | LLM 直接输出「独立/合并/拆分/重构」，同输入多次运行结果不稳定，Confidence 由模型自报 | v1.0.0 改为 Evidence Compiler + Repro Gate + Decision Engine；Confidence 由脚本计算 | 已修复 |
| 2026-08-08 | 语义证据引用 | 模型声称证据在 SKILL.md 第 20–24 行但行号不存在 | 新增 verify_evidence.py 机器验证 Anchor，无效证据自动降级 UNKNOWN | 已修复 |
| 2026-08-08 | 重复运行 | 相同输入每次重新生成裁决，无法证明 100 次一致 | 新增 Content-Addressed Cache：相同 AuditKey 直接返回 Certified Result | 已修复 |
| 2026-08-08 | 状态模型 | v1.0.0 把 INSUFFICIENT_EVIDENCE 当作 Lifecycle Decision 输出 | v1.1.0 正交化：lifecycle_decision=null / WITHHELD，INSUFFICIENT_EVIDENCE 只属于 Audit Status | 已修复 |
| 2026-08-08 | 语义一致性指标 | 未做独立语义复现仍输出 semantic_agreement=1.0 | v1.1.0 未传 --independent 时 semantic_agreement=null / UNVERIFIED | 已修复 |
| 2026-08-08 | 全局 UNKNOWN 门 | 任一字段 UNKNOWN 阻断全部 Lifecycle Decision | v1.1.0 按裁决定义 required_fields，只 WITHHOLD 关键证据 | 已修复 |
| 2026-08-08 | 快速排序指标缺失 | 只有裁决、没有健康分/成熟度/认证等级 | 新增 score_card.py 确定性计算 Health Score + Maturity L1-L5 + Certification C0-C4 | 已修复 |
| 2026-08-08 | 展示层是机器转写 | 顶部先展示 Hash、主表出现 0.9375、WITHHELD 机器枚举重复 | v1.2.0 Obsidian 人类决策视图：状态→问题→行动→技术证据，Hash 下沉折叠区 | 已修复 |
| 2026-08-08 | 健康分无状态标签 | 100 分可能造成「完美」错觉 | v1.2.0 增加 health_score_status（VERIFIED / PARTIAL / PROVISIONAL），PARTIAL 显示「暂定健康度」 | 已修复 |
| 2026-08-08 | 无 Provisional Direction | WITHHELD 时人类没有方向参考 | v1.2.0 decision_engine 输出候选方向，与正式裁决隔离 | 已修复 |
