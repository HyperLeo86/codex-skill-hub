# skill-analyst changelog

## 1.1（2026-08-07）

- 新增 Profile 模式：一键输出技能身份卡（核心目的/意图/逻辑/实现效果/重要场景/注意事项）
- 新增 references/profile-template.md 身份卡模板
- description 新增触发句「介绍一下这个 skill」「给我一张这个技能的身份卡」
- mode 枚举增加 profile；output-spec 增加身份卡输出规范

## 1.0.1（2026-08-07）

- 阶段 5 优化-验证循环加轮次上限（≤3 轮，超限交用户）
- 新增维护纪律：模型升级后全量回归 + 旧补丁可删性检查
- 新增 scripts/check_triggers.py 触发回归检查器
- mode 枚举统一：analysis.json 小写 quick/full/batch，正文展示 Quick/Full/Batch
- 补齐 CHANGELOG.md（版本纪律）
- 来源：skill-analyst 1.0.0 自检（P2-L6 / P2-E3 / P2-E4 / P3-L4 / P3-E2）

## 1.0.0（2026-08-07）

- 初版：四维体检（逻辑/可用性/可修改性/可进化）+ 六阶段工作流 + Quick/Full/Batch 三模式
- 资源：analyze_skill.py 静态事实收集器、checklist/scorecard/mode-map/output-spec、回归账本
- 按 skill-forge 契约流程创建，RED→GREEN 通过
