# 架构与职责分层（v0.2）

## 一条主链

Source of Truth → Semantic Compiler → Presentation IR (PIR) → Task View + Presentation Profile → Deterministic Renderer → Structural Gate → Human Readability Evaluation

## 分层职责表

| 层 | 职责 | 允许 LLM | 能否改事实 |
| --- | --- | --- | --- |
| Source of Truth | 数据库 / Agent JSON / 文件 / API / 原始报告 | — | 是（事实所在） |
| Semantic Compiler | 抽取 / Claim Identification / 语义分组 / 优先级 / 不确定性 / Provenance / Task Recognition | ✅ | 否（只转写，不新增事实；缺失标 ASSUMPTION） |
| Presentation IR (PIR) | 展示中间表示：Core PIR + Task View | — | 否 |
| Task View + Presentation Profile | 任务语义结构 + 用户/终端展示偏好 | — | 否 |
| Deterministic Renderer | 模板选择 / 字段映射 / 表格卡片 / 渐进披露 / Markdown | ❌ | 否 |
| Structural Gate | 结构性可读规范（确定性检查） | ❌ | 否 |
| Human Readability Evaluation | 人类是否快速定位 / 误读 / 知道下一步 | ✅（人/真实使用） | 否 |

## 三条硬性分离

1. **Source of Truth ≠ PIR**：PIR 是经过抽取、压缩、优先级判断、结构转换后的展示中间表示，天然可能存在信息损失；任何层不得把 PIR 宣称为原始事实本身。
2. **Compiler ≠ Renderer**：Compiler 允许 LLM（语义判断）；Renderer 禁止语义判断，只做「PIR + Profile + Task View → Markdown」的确定性映射。
3. **PIR ≠ Presentation Profile**：PIR 回答「信息是什么」，Profile 回答「怎么给这个人看」；用户偏好不得写进 PIR。

## 信息损失声明

Compiler 在压缩时可能丢弃原始细节；被丢弃的信息必须仍可在 Source 中定位（provenance 可追溯），并在 PIR 中记录「已压缩/已省略」的范围（如 technical.raw 或 relations）。

## v0.2 停止条件

不做：PDF / Dashboard / Semantic Zoom UI / Mobile / 流式渲染 / LLM-as-Judge / 图形自动生成 / Universal Ontology / 20 种模板 / 复杂 Profile 系统 / 多 Agent 编译。

完成 P0/P1 后停止理论设计，进入真实使用：收集 ≥10 类真实输出 + 20–30 次调用；失败 → Regression Case；普遍失败 → Rule Proposal；验证后再进 v0.3。
