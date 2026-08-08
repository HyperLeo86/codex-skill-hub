# 两种渲染方案对比

## 概览

**发生了什么**：方案 A 更快但覆盖终端少；方案 B 慢但覆盖多端。

| 项目 | 速度 | 多端支持 | 维护成本 |
| --- | --- | --- | --- |
| 方案 A | 快 | 1 端 | 低 |
| 方案 B | 中 | 3 端 | 中 |

## 关键差异

- 多端支持差异最大

## 权衡

- A 快但只支持单端
- B 慢但多端

## 推荐

先用 A 验证结构，再迁移到 B 多端

## 证据

| id | source_id | locator | detail | 状态 |
| --- | --- | --- | --- | --- |
| ev-1 | benchmark | bench/2026-08-08 | A=1.2s | ✅ |
| ev-2 | docs | docs/multi-endpoint | B 支持 3 端 | ✅ |

<details>
<summary>原始字段与技术元数据（L4）</summary>

- `profile`: `hyperleo-default`

</details>
