# skill-publisher changelog

## 1.0（2026-08-03）

- 首个版本：按「技能发布与版本管理规范」生成、校验、版本化并发布 Codex 技能
- 流程：输入处理 → 生成/更新 → 校验 → 保存 → 版本 → 发布 → 幂等复查
- 规范依据：agentskills.io + gh skill + 个人仓库实践（规范全文见 references/spec.md 与 Obsidian「我的skills」）

## 1.1（2026-08-03）

- 内嵌自动校验门：scripts/validate_skills.sh 一键运行 gh skill publish --fix + skills-ref validate（全库扫描）
- 发布流程更新：校验门双绿（gh skill + skills-ref）才允许 commit / tag / push
