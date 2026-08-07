# 回归账本（保留最近 10 条）

| 日期 | 场景 | 失败 | 修复 | 状态 |
| --- | --- | --- | --- | --- |
| 2026-08-07 | 发布 skill-forge v1.4 | validate_skills.sh 从安装副本调用时 REPO_DIR 解析到 ~/.codex/skills（非 git 仓库），校验门报错 | 1.3：git rev-parse --show-toplevel 自动探测 + 找不到仓库时明确报错 | 已修复（1.3 内建） |
| 2026-08-07 | 发布 skill-forge v1.4 | 校验门双绿但 push 认证失败（SSH agent 无身份 / PAT 无写权限），失败降级建议无效 | 1.3：新增 preflight_push.sh + 失败降级拆两条认证链 + 自动回退 ~/.ssh/neo/neo_git_ed25519 | 已修复（1.3 内建） |
| 2026-08-03 | 发布新技能 codex-1password-secrets | 发布后 README 技能清单未同步，新增技能未体现在仓库 README | 发布流程新增 update_readme.py 强制同步 + 验收项「README 清单与技能目录一致」 | 已修复 |
| 2026-08-07 | 发布 codex-1password-secrets v1.2 | git push 走 1Password SSH agent，未解锁报 sign_and_send_pubkey failed；HTTPS PAT 推送同样 403 | 改用 ~/.ssh/neo/neo_git_ed25519 一次性推送；提示 1Password 解锁后 SSH 恢复 | 已修复 |
