# 证据策略（Evidence Policy）

## 证据分层

1. Deterministic Facts：文件存在性、schema、manifest、引用、依赖、版本、结构一致性。由 static_checks.py 产生，禁止 LLM 判断。
2. Semantic Features：身份、价值、纯度、边界、生态位、行为的结构化抽取。由 LLM 按 protocol/semantic-schema.json 产生。
3. Evidence Anchors：语义字段引用的具体文件与行号。由 verify_evidence.py 机器验证。

## Anchor 验证规则

LLM 声称「证据在 SKILL.md 第 20–24 行」不能直接相信。必须验证：

- 文件存在
- 行号存在且在范围内
- quote_hash 与当前 snapshot 内容一致（若提供）
- evidence 与当前 evidence bundle 属于同一版本

无有效证据的字段自动降级为 UNKNOWN。

## UNKNOWN 规则

- 禁止为了稳定把 UNKNOWN 强改成 YES / NO。
- 无真实 usage 数据 → usage_frequency = UNKNOWN，禁止猜。
- 无法判断的字段进入 INSUFFICIENT_EVIDENCE，而不是由模型补全。

## 禁止项

- 不使用 Token 数、行数、Trigger 数量作为质量代理指标。
- 不建立总分。
- 不允许无证据推断。
- 不允许模型自报 Confidence；指标由脚本计算。

## 覆盖率与一致性指标

- snapshot_coverage：bundle 中存在的目标证据类型 / 期望证据类型（SKILL.md, spec.json, references, scripts, tests, protocol）。
- decision_evidence_coverage：Decision-Critical Fields 中 status=KNOWN 的比例。
- usage_coverage：usage_evidence 非空为 1.0，否则 0.0。
- behavior_coverage：behavior.test_suite_pass=true 为 1.0；有行为结果但未通过为 0.5；缺失为 0.0。
- reproducibility_coverage：独立语义复现已执行（STABLE 或 UNSTABLE）为 1.0，否则 0.0。
- semantic_agreement：未进行独立语义复现时为 null，禁止写成 1.0。

以上全部由脚本计算，LLM 不得自由评分。

## Health Score 状态标签

health_score_status 由 score_card.py 确定性计算，与分数一起输出：

- VERIFIED：health_score=100 且 decision_evidence_coverage=1.0（已验证，无关键缺口）
- PARTIAL：health_score=100 但关键证据未齐（例如 usage_frequency=UNKNOWN）
- PROVISIONAL：存在未通过的确定性检查项

PARTIAL / PROVISIONAL 时人类报告显示「暂定健康度」，避免 100 分产生「完美」错觉。

## Provisional Direction 与 Blockers

- provisional_direction 由 decision_engine.py 在 WITHHELD 时输出（KEEP/UPGRADE/MERGE/SPLIT/DEPRECATE 候选或 NONE）；只作人类参考，不属于正式 Lifecycle Decision，不触发治理动作。
- blockers 由 score_card.py 按 protocol/scoring.json 的固定定义生成，P1 优先；人类报告只展示 Top 3–5 条，其余下沉。
