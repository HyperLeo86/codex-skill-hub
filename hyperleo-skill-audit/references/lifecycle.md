# Lifecycle Decision 定义

## KEEP

当前形态合理，继续独立存在。

- 条件：Identity clear + Necessity established + Integrity acceptable + Boundary clean + Position unique + Behavior acceptable。
- 失效：任一前置字段为 UNKNOWN 或行为失败未修复。

## UPGRADE

身份与生态位成立，但实现、测试、规则或文档需要升级。

- 条件：identity_clear = YES 且 value_established = YES，且存在实质性缺陷（契约失败、行为失败、完整性不足或依赖不健康）。
- 失效：身份本身不成立（可能应 SPLIT / MERGE / 人工裁决）。

## MERGE

独立价值不足，与另一个 Skill 合并更合理。

- 条件：与邻居为 DUPLICATE / SUBSET，且 unique_value = NO。
- 必须说明 Merge with whom、为什么、保留哪些能力、删除哪些能力。

## SPLIT

内部存在两个或以上独立 Job。

- 条件：multiple_independent_jobs = YES 且 each_job_independent = YES。
- 必须说明拆成哪些能力、每个能力的独立 Intent、原 Skill 如何迁移。

## DEPRECATE

能力没有继续存在的必要。

- 条件：unique_value = NO 且 replaceability = HIGH 且 unique_assets = NO 且 usage_frequency != HIGH。
- 用途包括：被完全替代、价值消失、功能过于简单、长期无人使用、历史遗留。

## REBUILD 的归属

REBUILD 不再是第一级生命周期状态。它本质是 UPGRADE / major：保留 Intent，丢弃实现，整体重建。

## 统一规则

- 每个裁决只要求它自己的 required_fields：SPLIT 需要 multiple_independent_jobs/each_job_independent；MERGE 需要 duplicate_relationship/unique_value；DEPRECATE 与 KEEP 需要 usage_frequency；UPGRADE 需要身份/价值/缺陷字段。
- 关键证据缺失 → lifecycle_decision=null 且 lifecycle_status=WITHHELD，列出 missing_fields；非该裁决关键字段缺失不阻塞该裁决。
- INSUFFICIENT_EVIDENCE 只允许作为 Audit Status 出现，绝不作为 Lifecycle Decision。
- Decision Table 是优先级明确的规则树，不是加权评分。
- 所有正式裁决由 decision_engine.py 计算；LLM 不得直接输出。
