# CHANGELOG

## 1.1（2026-08-07）

- 重命名：prd-writer → hyperleo-prd-writer（HyperLeo 命名规范，非破坏性重命名）
- 版本 1.0 → 1.1

## 1.0（2026-08-05）

- 重命名：prd-writer → hyperleo-scribe-quill（HyperLeo 命名规范）
- 初版：示例驱动的可执行 PRD 撰写与审核技能
- 核心机制：三视角访谈 → 概念版 → 落地版（示例先行 + GWT AC）→ DoR 100 分闸门 → 纵横审核 → 交接包
- 交付物：PRD + RFI 日志 + 决策日志 + 假设索引 + 追溯矩阵
- 内置机械校验脚本：validate_prd.py（禁词/TBD/AC 可测性/规则缺例子）、traceability_check.py（孤儿需求/孤儿 AC）
