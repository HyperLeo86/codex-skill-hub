# skill-publisher changelog

## 1.4（2026-08-07）

- 重命名：skill-publisher → hyperleo-skill-publisher（HyperLeo 命名规范，非破坏性重命名）
- 版本 1.3 → 1.4

## 1.0（2026-08-03）

- 首个版本：按「技能发布与版本管理规范」生成、校验、版本化并发布 Codex 技能
- 流程：输入处理 → 生成/更新 → 校验 → 保存 → 版本 → 发布 → 幂等复查
- 规范依据：agentskills.io + gh skill + 个人仓库实践（规范全文见 references/spec.md 与 Obsidian「我的skills」）

## 1.1（2026-08-03）

- 内嵌自动校验门：scripts/validate_skills.sh 一键运行 gh skill publish --fix + skills-ref validate（全库扫描）
- 发布流程更新：校验门双绿（gh skill + skills-ref）才允许 commit / tag / push

## 1.2（2026-08-03）

- 新增 README 技能清单同步：scripts/update_readme.py 自动扫描技能目录并更新 README 表格（幂等，无变化不写文件）
- 发布流程新增第 6 步「同步 README」+ 对应验收与失败降级条款；规范升级 v1.2（Obsidian 与 references/spec.md 同步）

## 1.3（2026-08-07）

- 重命名：skill-publisher → hyperleo-raven-post（HyperLeo 命名规范）
- validate_skills.sh REPO_DIR 改为 git root 自动探测，不再依赖调用位置；找不到仓库时明确报错
- 新增 scripts/preflight_push.sh：发布前检测 remote 协议 / SSH agent / 回退钥匙 ~/.ssh/neo/neo_git_ed25519 / HTTPS 写权限
- 失败降级拆分为「校验认证」与「发布认证」两条链，各自附检测与修复指引
- 触发面限定为「创建后立即发布 / 更新后推送 / 同步」语义，反触发「纯创建不发布（走 skill-forge）」
- 幂等复查明确对比方法：git diff <tag> -- <skill-dir>
- spec.md 同步实际可见性（public）；升级流程加入 Preflight
- 账本种子化 2026-08-07 两起事故（REPO_DIR 路径依赖、发布认证链假设错误）
- 来源：skill-analyst 1.0.1 体检（建议重构发布子流程）
