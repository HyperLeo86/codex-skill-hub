# Position Anchor（生态位）

问题：为什么必须有这个独立 Skill？

## Positive
删除该 Skill 后，邻居无法完全接管其 Job；存在可描述的损失（能力、资产、流程、测试）。

## Negative
回答不了「如果删除，会损失什么」→ 强 MERGE / DEPRECATE 信号。

## Borderline
与邻居 OVERLAP，但各自拥有独特资产；关系按固定枚举记录。

## 判定规则
- 邻居必须通过可复现方式产生：用户指定 → registry 显式关系 → 固定相似度规则 → 固定版本 embedding。
- 选中的邻居列表必须进入 Evidence Bundle，邻居变化必须改变 evidence_bundle_hash。
- duplicate_relationship 只使用固定枚举：NONE / INDEPENDENT / COMPLEMENTARY / UPSTREAM / DOWNSTREAM / ALTERNATIVE / OVERLAP / SUBSET / DUPLICATE / UNKNOWN。
