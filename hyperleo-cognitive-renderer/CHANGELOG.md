# CHANGELOG

## 0.2.0（2026-08-08）

- 架构校正与职责分层（本轮只做架构，不做功能扩张）。
- PIR 取代 IR：明确 Source of Truth ≠ PIR；Protocol 数据驱动（protocol/pir-schema.json + task-views + presentation-profiles）。
- Outcome 与 Epistemic State 拆轴；derivation_type 让 ASSUMPTION 机器可识别。
- check_report.py → check_structure.py（Structural Readability Gate）；人类可读性评估单列 Layer B。
- Compiler（compiler/presentation_ir.py，允许 LLM）与 Renderer（scripts/render_md.py，确定性）模块分离。
- Task View + Presentation Profile 分层；实现 decision/diagnosis/comparison/monitor 四种真实模板，browse/learning 明确报错。
- tests/ 加入 golden / boundary / determinism 测试。
- 「3–5 秒理解」改为「3–5 秒 Time to Orientation」。

## 0.1.0（2026-08-08）

- 初始版本：契约驱动生成（skill-forge v1.5）。
- 核心能力：Canonical IR 契约 + 10 步渲染 SOP + 5 问探针 + 不确定性语义表 + 证据链 + L0–L4 渐进披露 + 多端渲染。
- 工具：`check_report.py`（IR 校验 + 探针）、`render_md.py`（IR → Markdown）。
- 验证：RED→GREEN 测试通过；示例 IR（assets/example_audit.json）渲染与探针全绿；A/B 前向测试待验证。
