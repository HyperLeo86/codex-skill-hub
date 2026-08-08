# Cognitive Fit 与 Task View（v0.2）

## 任务 → 视图映射

| Human Task | Task View | 默认表达 | 是否实现（v0.2） |
| --- | --- | --- | --- |
| decide | decision | 状态卡 + blocker + action | ✅ |
| diagnose | diagnosis | 问题卡 + 原因 + 下一步 | ✅（与 decision 同模板） |
| compare | comparison | 对比表 + trade-off + recommendation | ✅ |
| monitor | monitor | 状态表 + 变化 + 异常 + 行动 | ✅ |
| browse | browse | 分类 / 目录 | ❌ 未实现，明确报错 |
| learn | learning | 概念 + 顺序 + 深潜 | ❌ 未实现，明确报错 |

原则：**已实现 3 种，就明确说支持 3 种**（decision/diagnosis/comparison/monitor 共 4 种），不假装支持 6 种。

## Time to Orientation（3–5 秒）

不是「3–5 秒理解报告」，而是「3–5 秒完成定向」：

1. 这是什么？
2. 当前整体状态是什么？
3. 最重要的信息在哪里？
4. 是否有需要立即关注的问题？
5. 接下来应该从哪里继续看？

decide / monitor / diagnose 可进一步要求 3–5 秒识别「下一步动作」；learn 不要求 3–5 秒真正理解。
