---
name: prd-writer
description: >-
  示例驱动的可执行 PRD（产品需求文档）撰写与审核技能：三视角访谈 → 概念版对齐 → 落地版（每条规则配例子、AC 产出 GWT）→ DoR 100 分闸门 → 纵横审核 → 交接包（PRD + RFI 日志 + 决策日志 + 追溯矩阵），产出开发人员（人或 AI 编码 Agent）可无追问开工的文档。当用户说「帮我写 PRD / 需求文档 / 产品需求 / 功能文档 / 整理需求 / 从零写 PRD / 评审 PRD / 评估需求文档 / 把模糊想法变成可开发文档」，或甲方/业务方与开发方需要把模糊需求变成可开发、可验收的契约时使用；不用于头脑风暴、产品选题、商业模式设计。
---

# PRD Writer

**版本**：1.0（2026-08-05）

## 定位

在双方都不一定专业、且开发方需要兜底的场景下，把模糊业务意图变成「示例驱动的可执行契约」。核心机制是**例子即规格**：不要求甲方描述系统，只要求甲方对例子、边界、取舍做判断。

## 触发与反触发

- 触发：帮我写 PRD / 需求文档 / 产品需求 / 功能文档；整理需求；从零写 PRD；评审 PRD；评估/改进已有需求文档；把一句话想法变成可开发文档
- 反触发：头脑风暴、产品选题、商业模式设计、技术方案/系统设计文档（改走其他技能）

## 决定权（自由度 medium）

- 按 7 步工作流执行；问题措辞、例子细节、模板裁剪允许合理变化
- 用户显式指定模式（快速/标准/严格、完整版/迭代版）时以用户为准
- 例子与 AC 必须由用户确认；AI 不得把未确认内容写成事实

## 工作流

### 第 0 步：输入与模式识别

读入用户输入与已有草稿；判定模式 A（从零）/ B（评估改进）/ C（增量更新）、档位（完整/迭代）、模式（快速/标准/严格）。不适合则明确告知并停止。

### 第 1 步：三视角访谈

按 [interview-guide.md](references/interview-guide.md) 提问：用户视角（谁用、完成什么）、业务视角（目标、指标、边界）、技术视角（约束、集成、合规）。每轮 ≤3 问，确认型问题优先。记录写入工作区。

### 第 2 步：概念版 + 范围冻结

按 [concept-template.md](assets/concept-template.md) 产出概念版（核心用户 / 要解决的一件事 / 产品形态 / 结构 / MVP 功能 / 非范围 / 技术前提）。标准与严格模式必须先经用户确认；快速模式可用文首摘要代替。

### 第 3 步：落地版（示例先行）

按 [outline.md](references/outline.md) 展开 8 模块。硬规则：

- 每条业务规则配 1–3 个具体例子（[example-first.md](references/example-first.md)）
- AC 用 GWT 写（[acceptance-guide.md](references/acceptance-guide.md)）
- 禁止 TBD/待定；未确认信息进假设索引或开放问题
- 默认只展开 MVP 核心功能（MVP 闸门）

### 第 4 步：DoR 评分闸门

按 [quality-rubric.md](references/quality-rubric.md) 做 100 分制评分。阈值：快速 80 / 标准 90 / 严格 95。低于阈值不交付，只按最低分维度定向追问（每轮 ≤3 问）。

### 第 5 步：纵横审核 + 追溯检查

按 [review-standard.md](references/review-standard.md) 做纵向逐模块 + 横向七维审核；运行 `python3 scripts/traceability_check.py <PRD 路径> [acceptance-map.md]`。阻塞项与孤儿项清零才算通过。

### 第 6 步：交接包

交付到 `docs/`：

- `YYYY-MM-DD-<主题>-PRD.md` 主文档
- `rfi-log.md`（按 [rfi-protocol.md](references/rfi-protocol.md) 初始化）
- `decisions.md`（ADR 式决策日志）
- `assumptions.md`（假设索引）
- `acceptance-map.md`（需求↔AC↔测试追溯矩阵）

运行 `python3 scripts/validate_prd.py <PRD 路径>` 做机械初检。

## 验收

- DoR ≥ 阈值；禁词 = 0；无 TBD；每条规则 ≥1 例子；孤儿需求/孤儿 AC = 0
- 开发人员（或编码 Agent）开工前追问 ≤3，且追问项都在 RFI 日志/开放问题中已声明
- 变更全部走 RFI/变更单，口头变更 = 0

## 失败降级

- 甲方只给一句话且不配合访谈 → 先产出带 `[ASSUMPTION]` 标签的概念版，确认请求转下一轮
- 甲方对 RFI 不响应 → 按 [rfi-protocol.md](references/rfi-protocol.md) 默认假设机制处理并升级
- 用户要求快速出稿 → 快速模式：单文件 PRD + 文首概念摘要，跳过逐轮确认
- 校验失败 → 按报错修复后重跑，禁止放宽规则通过

## 资源

- 访谈题库：[interview-guide.md](references/interview-guide.md)
- 示例先行协议：[example-first.md](references/example-first.md)
- 8 模块骨架：[outline.md](references/outline.md)
- AC 写法：[acceptance-guide.md](references/acceptance-guide.md)
- 审核标准：[review-standard.md](references/review-standard.md)
- 评分卡：[quality-rubric.md](references/quality-rubric.md)
- RFI 协议：[rfi-protocol.md](references/rfi-protocol.md)
- 追溯矩阵：[traceability.md](references/traceability.md)
- 风格规范：[style-guide.md](references/style-guide.md)
- 正反例：[good-example.md](references/good-example.md)、[bad-example.md](references/bad-example.md)
- 模板：`assets/concept-template.md`、`assets/prd-template-full.md`、`assets/prd-template-iteration.md`、`assets/dor-scorecard.md`、`assets/rfi-log-template.md`
- 机械校验：`scripts/validate_prd.py`、`scripts/traceability_check.py`
- 回归账本：[regressions.md](references/regressions.md)
- 变更记录：`CHANGELOG.md`
