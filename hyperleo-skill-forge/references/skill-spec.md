# 一页契约模板

## 用途

写 SKILL.md 之前先填满本契约（≤1 页）。填不满的项就是下一步要问用户的问题。

```json
{
  "name": "meeting-notes-cleaner",
  "one_liner": "把凌乱会议记录整理成结构化摘要",
  "triggers": [
    "帮我把会议记录整理一下",
    "把这段速记转成干净的会议纪要",
    "整理 meeting notes",
    "给我一份结构化会议摘要",
    "会议记录太乱了帮我理一理",
    "把录音转写整理成纪要"
  ],
  "anti_triggers": ["翻译会议记录", "代写会议决策"],
  "input_output": {
    "input": "原始会议记录文本或文件路径",
    "output": "结构化摘要：议题 / 决策 / 待办（含负责人与期限）",
    "acceptance": [
      "每个待办都有负责人",
      "决策与原文一致，无新增事实",
      "输出 ≤500 词"
    ]
  },
  "freedom": "medium",
  "failure_modes": [
    {"scenario": "记录语言混杂", "fallback": "保留原语言，不强行统一"},
    {"scenario": "缺负责人信息", "fallback": "标「待确认」，不编造"},
    {"scenario": "输入为空", "fallback": "停止并询问，不生成空摘要"}
  ],
  "token_budget": {
    "skill_md_lines": 200,
    "skill_md_tokens": 1800,
    "references": ["output_format.md"]
  }
}
```

## 契约填写规则

1. `triggers` 至少 6 条，必须来自真实用户说法，不写书面语变体
2. `anti_triggers` 至少 1 条，防止误触发
3. `acceptance` 至少 3 条，必须可观察、可自动检查
4. `failure_modes` 至少 3 条，每条都有降级路径
5. `token_budget` 必填；超标时把内容拆进 `references/` 而不是压缩正文
6. `name` 必须为 `hyperleo-<单词>-<单词>`（最多 3 个单词），冰火/魔兽风格、kebab-case；由 check_skill.py 强制校验

## 自由度速查

| 自由度 | 适用 | 写法 | 生成器产出的决定权条款 |
| --- | --- | --- | --- |
| low | 顺序固定、易错 | 明确步骤或脚本 | 以脚本/步骤为准，禁止即兴偏离 |
| medium | 有偏好模式 | 伪代码 + 参数 | 按模板执行，参数可依上下文调整 |
| high | 开放任务 | 原则 + 简洁范例 | 只遵守原则与验收，路径自定 |
