# 技能身份卡模板（Profile 模式）

输出为 Markdown，六要素齐全，每项附证据位置。

```markdown
# <name> 身份卡

| 要素 | 内容 | 证据 |
| --- | --- | --- |
| 核心目的 | 一句话：它解决什么问题 | SKILL.md 概览 |
| 意图 | 为什么存在、想改变什么 | SKILL.md 定位/跃迁点 |
| 逻辑 | 步骤、决策门、核心机制 | 工作流章节 |
| 实现效果 | 实际产出、验收、边界 | 验收/输出物章节 |
| 重要场景 | 触发条件、最适用场景 | description + 触发章节 |
| 注意事项 | 已知坑、依赖、预算、维护状态 | 失败降级/资源/check 结果 |
```

## 补充信息（可选）

- 版本、行数/token、账本、脚本与引用存在性（来自 scripts/analyze_skill.py）
- 模式判断（Tool Wrapper / Generator / Reviewer / Inversion / Pipeline）
- 一句话总评（健康 / 需优化 / 建议重构，confidence）
