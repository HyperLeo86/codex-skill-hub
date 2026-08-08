# CHANGELOG

## 1.2（2026-08-08）

- Human Report 升级为 Obsidian 人类决策视图：固定结构（标题→总评→核心状态→能力审计→阻塞项→下一步→覆盖情况→生命周期→元数据→折叠技术详情）
- render_report.py 完全重写为确定性投影：状态翻译表、百分比取整、UNKNOWN/N/A 规则、Hash 下沉、<details> 折叠
- 新增 health_score_status（VERIFIED / PARTIAL / PROVISIONAL）：PARTIAL 显示「暂定健康度」，避免 100 分错觉
- 新增 provisional_direction（KEEP/UPGRADE/MERGE/SPLIT/DEPRECATE 候选），由 decision_engine.py 在 WITHHELD 时输出，与正式裁决隔离
- 新增 blockers / blocker_count / p1_blocker_count：score_card.py 按 scoring.json 固定定义生成，P1 优先
- Canonical Result 增加 dashboard 字段（skill_name / health_score_status / provisional_direction / blocker_count / p1_blocker_count / last_audit_at 等）

## 1.1（2026-08-08）

- Human Report Locale：machine schema 保持英文，人类报告默认 zh-CN，render_report.py 支持 --locale en
- 新增 Health Score 0–100：由 score_card.py 按 protocol/scoring.json 确定性计算，仅用于快速理解与排序，不参与 Lifecycle Decision
- 新增 Maturity Level L1–L5（Prototype / Structured / Tested / Governed / Certified）
- 新增 Certification Level C0–C4（NotCertified / EvidenceCollected / SemanticVerified / GovernedCalibrated / Certified），与 Maturity 分离
- 修正状态模型：audit_status 与 lifecycle_decision 严格正交；INSUFFICIENT_EVIDENCE 只属于 Audit Status；证据不足时 lifecycle_decision=null / WITHHELD
- 修正指标：未进行独立语义复现时 semantic_agreement=null；Evidence Coverage 拆分为 Snapshot / Decision Evidence / Usage / Behavior / Reproducibility 五类
- Decision Engine 改为按裁决定义 required_fields：只有缺失该裁决的关键证据才 WITHHOLD
- 新增 protocol/scoring.json 与 score_card.py；tests 增加 score_card / UNVERIFIED / WITHHELD 用例

## 1.0（2026-08-08）

- 重构为「可复现单体 Skill 治理审计」（Single Skill Governance / Reproducible Skill Audit）
- 新增 protocol/：protocol.yaml、semantic-schema.json、decision-rules.yaml、protocol.lock.json、anchors/（行为锚定量表）
- 新增 9 个确定性脚本：build_snapshot、static_checks、verify_evidence、compare_semantic_runs、decision_engine、protocol_hash、audit_cache、render_report、run_regression
- Lifecycle Decision 改为五枚举（KEEP / UPGRADE / MERGE / SPLIT / DEPRECATE）；REBUILD 并入 UPGRADE/major
- 新增 Audit Status（CERTIFIED / UNSTABLE / INSUFFICIENT_EVIDENCE / INVALID_INPUT / HUMAN_ADJUDICATED）
- 新增 Reproducibility Invariant 与 Content-Addressed Cache（AuditKey = SHA256(evidence_bundle_hash + protocol_hash)）
- 新增 tests/：unit、golden、boundary、regressions、calibration
- 移除 references/audit-card.md 与 purity-checklist.md（由 verdict-card.md 与 protocol/anchors/ 取代）

## 0.1.0（2026-08-08）

- 初版：LLM 直接输出裁决卡（独立 / 合并 / 拆分 / 重构）
