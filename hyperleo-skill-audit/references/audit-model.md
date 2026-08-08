# 审计模型（Audit Model）

## 定位

`hyperleo-skill-audit` 是三种属性的复合体：

1. Architecture Reviewer：判断身份、职责、价值、边界、生态位。
2. Measurement Instrument：统一量尺、证据、校准与协议版本。
3. Quality Gate：结果不满足稳定性或证据要求时，不允许强行输出裁决。

最高原则：LLM 可以参与理解，但不能拥有最终裁决权。

## 范式

旧模式：Skill → LLM 阅读 → LLM 思考 → LLM 输出裁决。

新模式：

Skill → Evidence Compiler → Deterministic Facts + Semantic Features → Reproducibility Gate → Deterministic Decision Engine → Certified Verdict Artifact。

核心跃迁：最终判断不直接依赖模型的一次采样。

## 五条宪法

1. Evidence before Judgment：没有证据，不判断。
2. Deterministic before Semantic：机器能确定的，永远不交给模型。
3. LLM Extracts; Rules Decide：模型负责理解与抽取，规则负责裁决。
4. Uncertainty Is a Valid Result：无法稳定判断就输出 Unknown / Unstable，禁止猜。
5. Same Evidence + Same Protocol = Same Certified Verdict：内容寻址、版本锁定、可复现。

## 两层结果必须分开

- Audit Status：本次审计本身是否可靠（CERTIFIED / UNSTABLE / INSUFFICIENT_EVIDENCE / INVALID_INPUT / HUMAN_ADJUDICATED）。
- Lifecycle Decision：Skill 应该怎么处理（KEEP / UPGRADE / MERGE / SPLIT / DEPRECATE，或 null / WITHHELD）。

只有 CERTIFIED 与 HUMAN_ADJUDICATED 允许 ISSUE Lifecycle Decision。
INSUFFICIENT_EVIDENCE 只属于 Audit Status，绝不作为 Lifecycle Decision。

## 三个独立标尺

1. Health Score（0–100）：由 score_card.py 按 protocol/scoring.json 的确定性权重计算，只用于快速理解与排序，不参与 Lifecycle Decision。
2. Maturity Level（L1 Prototype / L2 Structured / L3 Tested / L4 Governed / L5 Certified）：描述 Skill 自身质量到达的阶段。
3. Certification Level（C0 NotCertified / C1 EvidenceCollected / C2 SemanticVerified / C3 GovernedCalibrated / C4 Certified）：描述本次审计的证据与认证完成程度。

Maturity 与 Certification 刻意分开：一个高质量但从未被审计的 Skill 可以是 L4 + C0。

## 人类报告语言

Machine schema（JSON 字段、枚举）保持英文；人类可读报告由 render_report.py 按 --locale 输出，默认 zh-CN，可切换 en。

Human Report 是 Canonical Result 的确定性投影（Deterministic Projection），不是第二次审计：

- 固定结构：标题 → 一句话总评 → 核心状态 → 能力审计 → 当前阻塞项 → 下一步 → 覆盖情况 → 生命周期判断 → 审计元数据 → 折叠技术详情。
- 第一屏只回答：状态如何、成熟度、是否认证、生命周期方向、当前最大阻塞。
- Hash、协议、模型、seed、内部指标全部下沉到审计元数据或 `<details>`。
- Renderer 不得新增事实、不得重新解释、不得修改 Verdict、不得把 UNKNOWN 解释成 PASS/FAIL。
- 相同 audit-result.json 必须生成字节级一致的 Markdown。

## 底层世界模型

可类比四套成熟体系：编译器（模型只做前端 IR，后端确定性执行）、计量学（校准链 + 不确定度）、Reproducible Build（同输入同规则同产物）、软件 CI / Regression（升级必须证明无不可解释漂移）。
