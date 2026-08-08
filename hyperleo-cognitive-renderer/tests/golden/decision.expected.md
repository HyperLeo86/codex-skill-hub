# Skill Audit：hyperleo-intent-recognition

## ✅ HEALTHY · ⬜ 未测量

**发生了什么**：七维审计基本通过，但 Usage 与 Reproducibility 未验证，暂缓正式认证。

**状态**：HOLD
**原因**：缺 Usage 与 Reproducibility 证据
**风险**：未经验证的能力可能在实际任务中失效
**行动**：补齐 Usage 证据后重新认证

## 关键发现

- **[Critical]** Identity 与 Purity 通过，职责边界清晰 `VERIFIED` [ev-1](#证据)
- **[Critical]** Usage 未验证，无法证明被真实任务调用 `UNMEASURED` [ev-2](#证据)
- **[Important]** Reproducibility 未验证，无独立复现记录 `UNMEASURED` [ev-2](#证据)

## 证据

| id | source_id | locator | detail | 状态 |
| --- | --- | --- | --- | --- |
| ev-1 | SKILL.md | line 18-22 | single_job PASS | ✅ |
| ev-2 | audit-protocol | output.json | usage=0 · reproducibility=0 | ✅ |

<details>
<summary>原始字段与技术元数据（L4）</summary>

- `protocol_hash`: `abc123`
- `evidence_hash`: `def456`

```
snapshot=1.0; decision_evidence=0.9375; usage=0; reproducibility=0
```

</details>
