# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-07 | 技能分析（skill-analyst） | 步骤 10「上下文保护」排在归档后，语义倒置 | 改为跨切面规则（生效于步骤 3–9），不占步骤号 | 已修复（1.1 内建） |
| 2026-08-07 | 技能分析（skill-analyst） | 六层选型与五结论映射缺 BUY/INTEGRATE/EXTEND/COMPOSE/BUILD 的归属 | 决策表统一映射：直接用含 BUY/INTEGRATE；改改用含 EXTEND/COMPOSE；BUILD=自建 | 已修复（1.1 内建） |
| 2026-08-07 | 技能分析（skill-analyst） | Quick 模式未定义步骤映射，执行时无所适从 | Quick 明确走 0→1→3→4→7 | 已修复（1.1 内建） |
| 2026-08-07 | 技能分析（skill-analyst） | validation.md 引用不存在的 check_skill.py（死链） | 改为引用 skill-forge 的 check_skill.py | 已修复（1.1 内建） |
| 2026-08-07 | 技能分析（skill-analyst） | output-spec mode 枚举 normal 与 SKILL.md Full 不一致 | 统一为 quick/full/loop | 已修复（1.1 内建） |
| 2026-08-05 | PDF 选型（PyMuPDF vs pdfplumber） | 只看 stars 会漏 AGPL 合规后果 | M5 许可硬检查：AGPL/GPL/BSL 显式标注 | 已修复（1.0.0 内建） |
| 2026-08-05 | 检索完成但无结论 | 无 Verdict 行，结果不可执行 | M7 强制输出 Verdict 行 | 已修复（1.0.0 内建） |
| 2026-08-05 | 同主题二次检索 | 无历史归档导致重复劳动 | M2 历史库回灌 + 检索日志 | 已修复（1.0.0 内建） |
| 2026-08-05 | 用户说「别查了」 | 静默跳过，失去纠正窗口 | M7 跳过也输出一行 Verdict | 已修复（1.0.0 内建） |
| 2026-08-05 | 复杂任务内联搜索 | 原始输出淹没主上下文 | M10 Full 模式子代理蒸馏 | 已修复（1.0.0 内建） |
