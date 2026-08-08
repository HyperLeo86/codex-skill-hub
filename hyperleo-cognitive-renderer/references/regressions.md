# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-08 | v0.1→v0.2 架构评审 | check_report.py 名为「5 问探针」但只做结构检查，造成「结构合法 = 人类可读」的误认 | 改名 check_structure.py 为 Structural Gate；可读性评估单列 Layer B | 已修复 |
| 2026-08-08 | v0.1→v0.2 架构评审 | IR 称为「唯一事实源」，与上游 Source 混淆 | 改名 Presentation IR（PIR），声明 Source of Truth ≠ PIR | 已修复 |
| 2026-08-08 | v0.1→v0.2 架构评审 | PASS/FAIL/UNKNOWN 混在一个枚举，Outcome 与 Epistemic State 同轴 | 拆为 outcome + epistemic_state 双字段 | 已修复 |
| 2026-08-08 | v0.1→v0.2 架构评审 | 六种 task 只实现一种渲染结构，Cognitive Fit 停留在文档 | 实现 decision/diagnosis/comparison/monitor 四种真实 Renderer，browse/learning 明确报错 | 已修复 |
