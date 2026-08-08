# 失败模式与降级

## 明确禁止的 12 项设计

1. LLM 直接输出 Lifecycle Verdict
2. 用 Token 数判断成熟度
3. 用 Trigger 数量判断 Trigger 好坏
4. 用总分掩盖不同问题
5. 用模型自报 Confidence
6. 用多数投票掩盖规则不清
7. 为了稳定强迫 UNKNOWN 变成 YES/NO
8. Audit Memory 自动修改规则
9. 改变 Protocol 却保留相同 Protocol Hash
10. 重新随机生成已认证的 AuditKey
11. 把自然语言报告作为 Source of Truth
12. 声称 temperature=0 或 seed 保证真正确定性
13. Human Report 新增事实、二次裁决或重新解释审计结果（只允许确定性投影）

## 降级矩阵

| 场景 | 输出 | 动作 |
| --- | --- | --- |
| 目标路径不存在 / 缺 SKILL.md | INVALID_INPUT | 停止并询问，不猜路径 |
| 无法两次隔离 Semantic Extraction | reproducibility=UNVERIFIED、semantic_agreement=null | 不声称认证 |
| 裁决关键字段 UNKNOWN | lifecycle_decision=null / WITHHELD | 列出 missing_fields；非关键字段不阻塞 |
| 两次语义关键字段不一致 | UNSTABLE + 分歧清单 | 不输出裁决 |
| 无邻居 / 无使用记录 | 对应字段 UNKNOWN | 按证据门处理 |
| 被审计对象是自身 | 独立外部检查器 | 避免自我辩护偏差 |
| 新类型 Skill 无锚点 | UNKNOWN | 不强行一致 |
| Judge 升级后分布漂移 | 阻断发布 | 回滚协议版本 |
| INSUFFICIENT_EVIDENCE 被当作 Lifecycle Decision | 状态模型错误 | 只允许出现在 Audit Status |
| Human Report 展示 0.9375 / WITHHELD(WITHHELD) / 顶部 Hash | 展示层违规 | 百分比取整、状态翻译、Hash 下沉折叠区 |

## 不确定性的合法出口

Uncertainty 不是失败，是有效结果。CERTIFIED 之外的所有状态都允许存在，禁止用猜测填补。
