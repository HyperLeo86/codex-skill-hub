# 输出规范（skill-analyst）

## analysis.json 字段

```json
{
  "target": "绝对路径或名称",
  "mode": "quick | full | batch",
  "static_facts": {
    "lines": 0,
    "tokens": 0,
    "desc_chars": 0,
    "references": [],
    "scripts": [],
    "ledger": true
  },
  "dimensions": {
    "logic": {"passed": [], "issues": []},
    "usability": {"passed": [], "issues": []},
    "modifiability": {"passed": [], "issues": []},
    "evolution": {"passed": [], "issues": []}
  },
  "graph": "mermaid 源码字符串",
  "issues": [
    {
      "id": "P1-L4",
      "priority": "P1",
      "location": "SKILL.md:38",
      "problem": "两套选型词汇",
      "root_cause": "步骤 4 与决策表各写一套枚举",
      "evidence": "第 38 行 vs 第 47 行",
      "suggestion": "统一为一张映射表",
      "expected_effect": "执行时不再歧义"
    }
  ],
  "optimization_plan": [{"step": 1, "action": "……", "expected": "……"}],
  "eval_suggestions": ["……"],
  "verdict": "健康 | 需优化 | 建议重构 | 不建议直接用 | 待验证",
  "confidence": "HIGH | MEDIUM | LOW",
  "unverified": ["无法核验的结论清单"]
}
```

## 规则

- verdict 只允许五值；confidence 只允许三值
- mode 只允许小写 `quick | full | batch | profile`（正文展示 Quick/Full/Batch/Profile，JSON 一律小写）
- 每条 issue 必须有 location + evidence；无证据的结论放 unverified
- 节点图必须能由字符串直接渲染为 mermaid

## Profile 输出（身份卡）

Profile 模式输出 Markdown 身份卡，六要素：

```markdown
# <技能名> 身份卡

- 核心目的：一句话（它解决什么问题）
- 意图：为什么存在 / 想改变什么
- 逻辑：步骤 / 决策门 / 核心机制（可附简短流程）
- 实现效果：实际产出与边界
- 重要场景：什么情况下触发 / 最适用
- 注意事项：已知坑、依赖、预算与维护状态
```

规则：每个要素必须附证据位置（文件名/章节/行号）；无法核验的标注「待验证」。
