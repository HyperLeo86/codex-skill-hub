# 服务状态监控

## 监控概览

**发生了什么**：核心服务正常，一处缓存异常需要处理。

| 组件/指标 | 状态 |
| --- | --- |
| API | ✅ 正常 |
| 缓存 | ⚠️ 命中率 82% |
| 数据库 | ✅ 正常 |

## 变化

- 缓存命中率 95% → 82%

## 异常

- 缓存命中率低于阈值 85%

## 需要处理

- 检查缓存配置或扩容

## 证据

| id | source_id | locator | detail | 状态 |
| --- | --- | --- | --- | --- |
| ev-1 | health-check | GET /health | 200 OK | ✅ |
| ev-2 | metrics | metrics/cache-hit | 命中率 95% → 82% | ✅ |

<details>
<summary>原始字段与技术元数据（L4）</summary>

- `service`: `api-gateway`

</details>
