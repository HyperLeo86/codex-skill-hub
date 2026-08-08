---
name: hyperleo-cognitive-renderer
description: 将机器信息编译为与人类当前任务和认知方式匹配的高信噪比视图，同时保留事实、不确定性与证据链（Human Information Compilation Pipeline：Compiler → PIR → Task View + Profile → Renderer → Structural Gate）。当用户说 「把这份机器输出整理成人类可读的报告」；「这个结果太乱了，帮我重新组织成能快速看的界面」；「把数据库返回的结构化信息变成人能看懂的卡片」；「用认知渲染器把这个分析结果渲染一下」；「帮我规范 Agent 报告的输出格式」；「这份状态数据按可读性规范重新渲染」；「把复杂信息做成 3 秒能看懂的状态卡」 时使用；不用于：生成海报/图片/PPT 视觉稿（走 imagegen / presentations）、修改底层数据源或业务逻辑（本技能只渲染，不改事实）。
---

# hyperleo-cognitive-renderer

**版本**：0.2.0（2026-08-08）

## 概览

将机器信息编译为与人类当前任务和认知方式匹配的高信噪比视图，同时保留事实、不确定性与证据链。v0.2 只做架构校正与职责分层，不增加功能。

## 架构（一条主链）

Source of Truth → Semantic Compiler → Presentation IR (PIR) → Task View + Presentation Profile → Deterministic Renderer → Structural Gate → Human Readability Evaluation

- Source of Truth ≠ PIR：PIR 是展示中间表示，可能存在信息损失。
- Compiler 允许 LLM；Renderer 禁止语义判断。
- 相同 PIR + Profile 必须产生相同 Markdown。
- 分层原则详见 references/architecture.md。

## 触发与反触发

- 触发：把这份机器输出整理成人类可读的报告；这个结果太乱了，帮我重新组织成能快速看的界面；把数据库返回的结构化信息变成人能看懂的卡片；用认知渲染器把这个分析结果渲染一下；帮我规范 Agent 报告的输出格式；这份状态数据按可读性规范重新渲染；把复杂信息做成 3 秒能看懂的状态卡
- 反触发：生成海报/图片/PPT 视觉稿（走 imagegen / presentations）；修改底层数据源或业务逻辑（本技能只渲染，不改事实）

## 决定权（自由度 medium）

- 按协议/模板执行，参数可依上下文调整
- Compiler 层允许 LLM 判断（抽取/分组/优先级/任务识别）；Renderer 层必须确定性
- 输出格式遵循模板，内容允许合理变化

## 工作流（Phase A Compile → B Render → C Validate）

### Phase A — Compile（允许 LLM）

1. Detect Input：原始文本 / DB / Agent JSON / 文件 / API
2. Identify Human Task：browse / compare / diagnose / decide / learn / monitor
3. Extract Claims：拆成 claim，标注 derivation_type（DIRECT_FACT / DERIVED / INTERPRETATION / ASSUMPTION）
4. Preserve Provenance：每条 claim 关联 evidence（source_id / locator / snapshot / content_hash）
5. Classify Uncertainty：Outcome（业务结果）与 Epistemic State（VERIFIED / UNKNOWN / UNMEASURED / UNSTABLE / UNVERIFIED / N/A）分开标注
6. Determine Priority：critical / important / supporting / technical
7. Build Presentation IR：Core PIR（meta / summary / claims / evidence / relations / uncertainty）+ Task View

辅助：compiler/presentation_ir.py；PIR 契约：protocol/pir-schema.json

### Phase B — Render（必须确定性）

8. Load Presentation Profile：默认 protocol/presentation-profiles/hyperleo-default.yaml
9. Select Task View：按 view.type 选择模板
10. Apply Cognitive Fit：任务 → 表达映射（references/cognitive-fit.md）
11. Build Information Hierarchy：L0 状态行 → L1 决策/发现 → L2 证据 → L3 原始字段
12. Progressive Disclosure：技术细节默认折叠
13. Deterministic Rendering：scripts/render_md.py + templates/*

支持视图：decision / diagnosis / comparison / monitor；browse / learning 明确报错。

### Phase C — Validate

14. Structural Gate：scripts/check_structure.py 100% 通过（确定性、可重复、CI 友好）
15. Task Probe + Common Probe：按任务检查可读性（references/readability.md）
16. Deliver：输出 Markdown；PIR 保留为渲染输入

## 验收（来自契约）

- check_structure.py（Structural Gate）100% 通过
- Outcome 与 Epistemic State 分离；ASSUMPTION 机器可识别（derivation_type）
- 相同 PIR + Presentation Profile → 完全一致的 Markdown（确定性）
- 3–5 秒 Time to Orientation（这是什么 / 整体状态 / 最重要信息 / 需关注问题 / 从哪继续看）
- 支持视图明确声明：decision / diagnosis / comparison / monitor；browse / learning 报错不渲染

## 失败降级

- 输入无 schema（原始文本）→ 先经 Compiler 抽取为 PIR；缺失字段标 ASSUMPTION
- view.type 为 browse / learning → 明确报错「v0.2 未实现」，不强行渲染
- 证据缺失 / 不可追溯 → epistemic_state=UNVERIFIED，不编造 locator / hash
- Structural Gate 不通过 → 回 Phase A/B 修复，最多 2 轮；仍不过输出草稿 + 失败清单，标「待验证」
- Profile 缺失 → 使用 hyperleo-default

## 本轮停止条件（v0.2 明确不做）

PDF / Dashboard / Semantic Zoom UI / Mobile / 流式渲染 / LLM-as-Judge / 图形自动生成 / Universal Ontology / 20 种模板 / 复杂 Profile 系统 / 多 Agent 编译。
真实使用收集 ≥10 类输出 + 20–30 次调用后再进 v0.3。

## 资源

- compiler/presentation_ir.py：Compiler 辅助模块（LLM 可调用）
- protocol/pir-schema.json：PIR 契约（数据驱动校验源）
- protocol/task-views/*.json：decision / comparison / monitor 视图定义
- protocol/presentation-profiles/hyperleo-default.yaml：默认展示 Profile
- scripts/check_structure.py：Structural Gate（确定性）
- scripts/render_md.py：确定性渲染器
- templates/*.md：decision / comparison / monitor 模板
- references/architecture.md：主链与分层原则
- references/cognitive-fit.md：任务→表达映射
- references/uncertainty.md：Outcome / Epistemic 双轴 + 禁止映射
- references/provenance.md：证据链与 PIR≠事实源
- references/rendering-rules.md：渲染纪律 + 噪音清单
- references/readability.md：两层验证 + Common / Task Probe
- references/regressions.md：失败账本
- tests/：golden / boundary / regressions（tests/run_tests.py）
- assets/examples/：三类示例 PIR

## Token 预算（契约：240 行 / 2300 token）
