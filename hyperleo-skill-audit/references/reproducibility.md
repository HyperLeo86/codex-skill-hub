# 可复现性（Reproducibility）

## Reproducibility Invariant

同一个 Evidence Bundle + 同一个 Audit Protocol → 唯一 Canonical Audit Result。

正式形式：

AuditKey = SHA256(evidence_bundle_hash + protocol_hash)

AuditKey 相同 → Canonical Verdict 必须相同。

注意：这里保证的是「系统正式发布的审计结果可复现」，不是「裸 LLM 调用 100 次输出完全一致」。

## Content-Addressed Audit

1. 生成 Evidence Bundle（目标文件快照 + 邻居快照 + 行为测试 + 使用记录）→ evidence_bundle_hash。
2. 计算 Protocol Hash（rubric + semantic schema + anchors + decision rules + validator version + judge model + calibration version）。
3. audit_key = hash(evidence_bundle_hash + protocol_hash)。
4. 运行前先查历史认证缓存；相同 AuditKey 直接返回已认证 Canonical Verdict，禁止重新随机生成。

因此同一 Skill + 同一证据 + 同一规则运行 100 次，实际返回同一个认证产物。

## Reproducibility Gate

两个独立 Semantic Extraction 只比较 Decision-Critical Fields；全部一致 → STABLE，任一不同 → UNSTABLE。

- 禁止「三次投票取多数」：分歧本身就是审计结果。
- 无法做两次隔离模型调用 → reproducibility = UNVERIFIED，不得声称通过认证。
- 未进行独立语义复现时 semantic_agreement=null、reproducibility_coverage=0；禁止用同源两次运行的结果伪装成 1.0。

## 100 次一致怎么验证

- Runtime：首次认证 A/B 两次抽取；认证后相同 AuditKey 直接读缓存，复杂度 O(1)。
- Protocol Qualification：发布协议时对边界 Calibration Cases 做 20 / 50 / 100 次压力测试，证明测量仪器本身稳定。

## 协议升级

- 任何 Decision-Critical 内容变化必须改变 protocol_hash，产生新 AuditKey。
- 旧审计结果不得被新协议覆盖。
- Migration Test 必须逐条对比 per-item transition（从什么改成什么、为什么），不能只看总体分布。

## 分布指标

Lifecycle Decision 不是连续变量，不用 Wasserstein；使用 exact item transition、confusion matrix、total variation distance、Jensen-Shannon divergence。它们只是诊断指标；per-item exact match = 100% 时，分布不变性自然成立。

## 不要做的事情

- 不要声称 temperature=0 或 seed 可以保证真正确定性。
- 不要重新随机生成已存在 Certified Result 的 AuditKey。
- 不要让 Audit Memory 静默修改协议；规则变化必须走版本化流程。
