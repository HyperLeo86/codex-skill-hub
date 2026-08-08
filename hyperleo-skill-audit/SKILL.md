---
name: hyperleo-skill-audit
description: 把一个 Skill 当成具有身份、价值、契约、行为、边界、依赖和生命周期的软件能力单元，通过可复现的审计协议生成唯一、可追溯、可验证的治理裁决。当用户说 「审视一下这个 skill 合不合理」；「这个 skill 纯粹吗」；「这个技能职责是不是太多了」；「检查一下这个 skill 是否解耦」；「这个 skill 有没有独立的生态位」；「两个 skill 是不是重叠了，该不该合并」；「帮我判断这个技能该独立还是该拆」；「审一下这个 skill 有没有独立意图」 时使用；不用于：对 skill 做四维健康体检与优化方案（走 skill-analyst）、创建/升级技能本体（走 skill-forge）、把技能发布到 GitHub（走 skill-publisher）、修复或修改目标 skill 的内容（审计只读）。
---

# hyperleo-skill-audit

**版本**：1.2（2026-08-08）

## 定位

把一个 Skill 当成具有身份、价值、契约、行为、边界、依赖和生命周期的软件能力单元，通过可复现的审计协议生成唯一、可追溯、可验证的治理裁决。

三种属性：Architecture Reviewer（架构评审）、Measurement Instrument（测量仪器）、Quality Gate（质量闸门）。

最高原则：LLM 可以参与理解，但不能拥有最终裁决权。

## 触发与反触发

- 触发：审视一下这个 skill 合不合理；这个 skill 纯粹吗；这个技能职责是不是太多了；检查一下这个 skill 是否解耦；这个 skill 有没有独立的生态位；两个 skill 是不是重叠了，该不该合并；帮我判断这个技能该独立还是该拆；审一下这个 skill 有没有独立意图；帮我审计一下这个 skill；这个 skill 应该升级还是拆分；给这个 skill 出一份审计卡；用审计协议跑一遍这个技能
- 反触发：对 skill 做四维健康体检与优化方案（走 skill-analyst）；创建/升级技能本体（走 skill-forge）；把技能发布到 GitHub（走 skill-publisher）；修复或修改目标 skill 的内容（审计只读）

## 决定权（自由度 medium）

- 按协议与脚本执行：阶段顺序固定，参数可依上下文调整
- 脚本输出是唯一事实源：禁止覆盖或重算脚本结果
- LLM 只做 Semantic Feature Extraction，禁止输出 Lifecycle Decision、总分或自报 Confidence
- 正式结果以 audit-result.json 为准；Markdown 必须由 render_report.py 生成
- 人类报告默认按用户语言 zh-CN 输出（--locale en 可切换）；machine schema 保持英文
- Human Report 是 Canonical Result 的确定性投影：固定结构、不新增事实、不二次裁决

## 工作流（Orchestration）

产物写入本次任务目录的 `.audit/<skill-name>/<audit-key>/`；先运行 `scripts/protocol_hash.py` 得到 Protocol Hash，再按序执行：

1. Snapshot：`python3 scripts/build_snapshot.py --target <skill> --neighbors <n...> --usage <u...> --out .../evidence-bundle.json`
2. Cache Lookup：`python3 scripts/audit_cache.py --evidence-hash <E> --protocol-hash <P> --cache-dir <CACHE> --get`；命中直接返回 Certified Result，禁止重新生成。
3. Static Facts：`python3 scripts/static_checks.py --bundle .../evidence-bundle.json --facts-out .../facts.json`
4. Semantic Extraction ×2（LLM）：按 `protocol/semantic-schema.json` 与 `protocol/anchors/` 抽取，输出 semantic-run-a.json / semantic-run-b.json；每个字段带 evidence anchors（file / line_start / line_end / quote_hash）。
5. Evidence Verification：`python3 scripts/verify_evidence.py --target <skill> --semantic .../semantic-run-a.json --out .../verified-a.json`（A/B 各一次）
6. Repro Gate：`python3 scripts/compare_semantic_runs.py --run-a .../verified-a.json --run-b .../verified-b.json --critical-fields protocol/semantic-schema.json --out .../repro.json`；UNSTABLE → 输出 UNSTABLE + 分歧清单并终止，禁止多数投票。
7. Decision Engine：`python3 scripts/decision_engine.py --features .../verified-a.json --facts .../facts.json --behavior .../behavior.json --audit-status CERTIFIED --out .../decision.json`；每个裁决只要求它自己的 required_fields，关键证据缺失时 lifecycle_decision=null / WITHHELD。
8. Score Card：`python3 scripts/score_card.py --bundle .../evidence-bundle.json --facts .../facts.json --features .../verified-a.json --repro .../repro.json --behavior .../behavior.json [--independent-repro] [--certified] --out .../score.json`；输出 Health Score（0–100，不参与裁决）、Maturity L1–L5、Certification C0–C4 与五类覆盖率。
9. Impact：生成 impact.json（谁调用它、它调用谁、哪些 workflow / tests 受影响；只描述，不执行修改）。
10. Artifact：组装 audit-result.json（含 score.json 指标与 dashboard 字段：health_score_status / provisional_direction / blockers / 覆盖率 / last_audit_at）→ `python3 scripts/render_report.py --result .../audit-result.json --out .../audit-result.md --locale zh-CN`（Obsidian 人类决策视图，固定结构见 references/verdict-card.md）→ `python3 scripts/audit_cache.py ... --store .../audit-result.json`

## 验收（来自契约）

- 同一 Evidence Bundle + 同一 Protocol 必须对应同一 AuditKey；相同 AuditKey 必须返回同一 Certified Result，禁止重新随机生成
- Lifecycle Decision 只由 decision_engine.py 按 decision-rules.yaml 计算；关键证据不足时 lifecycle_decision=null 且 lifecycle_status=WITHHELD
- audit_status 与 lifecycle_decision 严格正交；INSUFFICIENT_EVIDENCE 只允许出现在 Audit Status
- Health Score 由 score_card.py 按 protocol/scoring.json 确定性计算，仅用于快速理解与排序，不参与裁决
- 未进行独立语义复现时 semantic_agreement=null；Evidence Coverage 拆分为 Snapshot / Decision Evidence / Usage / Behavior / Reproducibility 五类
- Human Report 按固定 Obsidian 结构生成（状态→问题→行动→技术证据）；Hash 下沉到审计元数据，不得新增事实或二次裁决
- 每个 Decision-Critical 语义字段必须有机器验证过的 Evidence Anchor，否则降级为 UNKNOWN
- Reproducibility Gate 只比较 Decision-Critical Fields；不一致时输出 UNSTABLE，禁止多数投票
- Audit 只读目标 Skill；动态产物写入 .audit/<skill>/<audit-key>/，不写入 Skill 本体
- audit-result.md 必须由 render_report.py 从 audit-result.json 确定性生成

## 失败降级

- 目标路径不存在或缺少 SKILL.md → 输出 INVALID_INPUT 与缺失清单，停止并询问，不猜测路径
- 无法进行两次隔离 Semantic Extraction → reproducibility=UNVERIFIED，禁止声称已通过复现认证
- 某个 Lifecycle Decision 的关键证据为 UNKNOWN → lifecycle_decision=null / WITHHELD，列出 missing_fields；非该裁决关键字段缺失不阻塞
- 两次语义运行关键字段不一致 → 输出 UNSTABLE 与分歧清单，不输出 Lifecycle Decision
- 无同级参照目录或使用记录 → 邻居与频率标 UNKNOWN，按证据门处理，不猜测
- 被审计对象是本技能自身 → 使用独立外部检查器与清单，避免自我辩护偏差

## 资源

- protocol/：protocol.yaml、semantic-schema.json、decision-rules.yaml、protocol.lock.json、anchors/
- scripts/：确定性逻辑（build_snapshot / static_checks / verify_evidence / compare_semantic_runs / decision_engine / score_card / protocol_hash / audit_cache / render_report / run_regression）
- references/：audit-model、lifecycle、evidence-policy、reproducibility、failure-modes、verdict-card、regressions
- tests/：unit、golden、boundary、regressions、calibration

## Token 预算（契约：260 行 / 2200 token）
