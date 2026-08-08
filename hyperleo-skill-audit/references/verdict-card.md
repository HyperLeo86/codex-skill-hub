# Obsidian 人类报告模板（固定结构）

audit-result.md 由 render_report.py 从 audit-result.json 确定性生成。
本模板顺序永久固定，所有 Skill Audit 使用同一结构，形成视觉肌肉记忆。

```markdown
# 🧩 Skill Audit · `<skill-name>`

> **当前判断：** <自动压缩的一句话总评；含总体质量 / 阶段 / 最大阻塞>

## 核心状态

| 指标 | 状态 | 说明 |
| --- | ---: | --- |
| **已验证健康度** | **100 / 100** | 已验证质量项全部通过 |
| **证据完整度** | **94%** | 缺少真实 usage 证据 |
| **成熟度** | **L4 · 治理级** | 已达到完整治理阶段 |
| **认证等级** | **C1 · 已收集证据** | 尚未通过独立复现认证 |
| **生命周期** | **⏸ 暂缓裁决** | 关键证据不足 |

## 能力审计

| 维度 | 状态 | 关键判断 |
| --- | :-: | --- |
| Identity 身份 | ✅ | One Job 清晰 |
| Necessity 必要性 | ⚠️ | 缺少真实使用频次数据 |
| Integrity 完整性 | ✅ | 确定性结构检查全部通过 |
| Purity 纯粹性 | ✅ | 工作流围绕单一核心 Job |
| Boundary 边界 | ✅ | 与相邻 Skill 分工明确 |
| Position 生态位 | ✅ | 与 skill-analyst 为互补关系 |
| Behavior 行为 | ✅ | Golden / Boundary / Regression 测试通过 |

## 当前阻塞项

| 优先级 | 缺口 | 影响 |
| :---: | --- | --- |
| **P1** | 缺少真实 Usage Evidence | 无法判断长期必要性 |
| **P1** | 未完成独立语义复现 | 无法升级为正式认证状态 |
| P2 | Self-Audit 同源偏差 | 建议由独立 Agent / 人工复核 |

> **下一步：** <1–3 个具体动作>。

## 覆盖情况

| 证据类型 | 覆盖率 |
| --- | ---: |
| Skill 快照 | **100%** |
| 决策证据 | **94%** |
| 行为测试 | **100%** |
| Usage 数据 | **0%** |
| 独立复现 | **0%** |

## 生命周期判断

**当前状态：⏸ 暂缓裁决**

不是因为 Skill 存在明显质量问题，而是正式生命周期裁决所需证据尚未全部满足。

当前已知证据更支持：**KEEP 候选**（Provisional Direction，仅参考，不触发治理动作）

但在完成认证之前，不将其记录为正式 Lifecycle Decision。

**关键事实：**（2–5 条，只保留影响当前结果的事实）

## 审计元数据

| 字段 | 值 |
| --- | --- |
| Protocol | `1.2.0` |
| Protocol Hash | `<hash>` |
| Audit Key | `<key>` |
| Audit Status | `<enum>`（<中文状态>） |
| Semantic Agreement | `N/A`（未独立复现时为 N/A，不得写 0% 或 100%） |

<details>
<summary>查看技术说明</summary>

- machine 字段：audit_status / lifecycle_decision / lifecycle_status / withheld_reason / missing_fields / provisional_direction
- reproducibility / semantic_agreement / health_score_status / blocker_count / p1_blocker_count / metrics（原始机器数值）
- 正式 Canonical Result 以 audit-result.json 为准；本报告为确定性投影，不产生新事实

</details>
```

## 展示规则（Renderer 固定实现）

- 状态翻译表：CERTIFIED→✅ 已认证；INSUFFICIENT_EVIDENCE→⚠️ 证据不足；UNSTABLE→⚠️ 结果不稳定；INVALID_INPUT→❌ 输入无效；WITHHELD→⏸ 暂缓裁决。
- 成熟度：L1 原型 / L2 结构化 / L3 可测试 / L4 治理级 / L5 认证级；主表缩写为 `L4 · 治理级`。
- 认证等级：C0 未审计 / C1 已收集证据 / C2 已完成语义验证 / C3 已通过复现验证 / C4 生产级认证。
- 百分比取整（0.9375 → 94%）；UNKNOWN 显示「未获得 / N/A」，不显示 0 分。
- Emoji 只允许 ✅ ⚠️ ❌ ⏸ 🧩 ❔；去掉 emoji 后报告仍完整可读。
- 首屏禁止出现 Hash 与底层实现细节；Hash 只出现在审计元数据与折叠区。
- 相同 audit-result.json 必须生成字节级一致的 Markdown。
