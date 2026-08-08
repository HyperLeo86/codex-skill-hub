# 不确定性双轴模型（v0.2）

## 两个维度不再混轴

| 轴 | 含义 | 示例 |
| --- | --- | --- |
| Outcome | 事情本身怎么样（业务枚举，随 Task View 变化） | HEALTHY / CONCERN / FAILURE；KEEP / UPGRADE / MERGE / SPLIT / DEPRECATE；POSITIVE / NEGATIVE / NEUTRAL / HOLD / N/A |
| Epistemic State | 我们是否知道、测过、验证过 | VERIFIED / UNKNOWN / UNMEASURED / UNSTABLE / UNVERIFIED / N/A |

人类层示例：

```json
{"outcome": "HEALTHY", "epistemic_state": "UNMEASURED"}
```

→ 显示「整体健康 · 部分证据未验证」。

## Epistemic State 语义

| 状态 | 含义 | 显示 |
| --- | --- | --- |
| VERIFIED | 已验证 | 已验证 |
| UNKNOWN | 存在但未知 | 未知 |
| UNMEASURED | 未测量/未测试 | 未测量 |
| UNSTABLE | 不稳定 | 不稳定 |
| UNVERIFIED | 证据缺失，未核验 | 未验证 |
| N/A | 不适用 | 不适用 |

## derivation_type（机器可识别的事实来源）

| 类型 | 含义 | 证据要求 |
| --- | --- | --- |
| DIRECT_FACT | 直接来自 Source 的事实 | 必须有 evidence |
| DERIVED | 由多个事实推导 | 必须有 evidence |
| INTERPRETATION | 解释 / 判断 | 必须有 evidence |
| ASSUMPTION | 假设，未证实 | 可不带 evidence，但必须机器可识别（用于统计/过滤/提醒/渲染/验证） |

## 禁止映射

- UNKNOWN / UNMEASURED → FAIL / FAILURE / NEGATIVE / DEPRECATE（Structural Gate 拦截）
- 未测量 ≠ 差；未知 ≠ 失败；不稳定 ≠ 失败（只能警告）
- 缺失证据 → 编造 locator / hash（必须标 UNVERIFIED）
- ASSUMPTION 只写在文字里（必须用 derivation_type 字段）
