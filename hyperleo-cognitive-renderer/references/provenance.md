# Provenance 与证据链（v0.2）

## PIR ≠ 事实源

PIR 是展示中间表示。真实事实在 Source（数据库 / Agent JSON / 文件 / API / 原始报告）。因此每个 PIR 必须声明 `meta.source`，每个结论必须能向下追溯。

## Evidence Schema（v0.2）

```json
{
  "id": "ev-1",
  "source_id": "SKILL.md",
  "source_type": "file",
  "locator": "line 18-22",
  "content_hash": "sha256:abc",
  "snapshot": "v0.1.0",
  "captured_at": "2026-08-08",
  "verified": true
}
```

必填：`id` / `source_id` / `locator` / `verified`。
建议逐步补充：`source_type` / `content_hash` / `snapshot` / `captured_at`（v0.2 不强校验，schema 已留位）。

## 追溯链

```
结论（claim）
  ↓ evidence.id
  ↓ source_id + locator
  ↓ snapshot / content_hash
原始 Source
```

## 规则

- 每个非 ASSUMPTION 的 claim 必须有 evidence 指针；缺证据标 UNVERIFIED。
- ASSUMPTION 用 `derivation_type: ASSUMPTION` 机器可识别，不以 `[ASSUMPTION]` 文字代替。
- Renderer 不创建、不合并、不猜测任何 claim / evidence。
