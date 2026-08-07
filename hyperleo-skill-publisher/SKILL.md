---
name: hyperleo-skill-publisher
description: 按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub。当用户说 「把 xxx 做成一个 skill 并发布」；「生成一个新技能并发布到 GitHub」；「发布这个 skill」；「按规范创建技能并打版本 tag」；「更新技能版本并推送」；「把本地技能同步到 codex-skill-hub」 时使用；在创建/升级技能后的发布、打 tag、同步仓库流程中自动接续使用。不用于：纯创建不发布（走 hyperleo-skill-forge）、市场调研或竞品分析、修改 MCP 服务器或插件清单、只写说明文档不创建技能。
---

# skill-publisher

**版本**：1.4（2026-08-07）

## 概览

按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub

## 触发与反触发

- 触发：把 xxx 做成一个 skill 并发布；生成一个新技能并发布到 GitHub；发布这个 skill；按规范创建技能并打版本 tag；更新技能版本并推送；把本地技能同步到 codex-skill-hub
- 反触发：纯创建不发布（走 hyperleo-skill-forge）；市场调研或竞品分析；修改 MCP 服务器或插件清单；只写说明文档不创建技能

## 决定权（自由度 medium）

- 按伪代码/模板执行，参数可依上下文调整
- 输出格式遵循模板，内容允许合理变化

## 工作流

1. **输入处理**：确认是新技能还是更新已有技能；先读 `references/spec.md`（规范）与 `references/regressions.md`（账本），命中已知失败模式必须写防复发条款。
2. **生成/更新**：新技能先写一页契约 `spec.json`（triggers ≥6、anti_triggers ≥1、acceptance ≥3、failure_modes ≥3、token_budget），再按契约生成 SKILL.md 骨架并填充程序性知识；已有技能直接定位目录做增量修改。
3. **校验（自动门）**：先运行 `scripts/validate_skills.sh [仓库目录]`——脚本自动用 `git rev-parse --show-toplevel` 探测仓库根（不依赖调用位置；探测失败会明确报错）；内置 `gh skill publish --fix`（GitHub 官方 agentskills 校验 + 安全检查）与 `skills-ref validate`（全库逐技能校验）双保险，全绿才允许继续；再运行 `check_skill.py <dir> [spec.json]` 做结构/token/账本检查，要求 name=目录名、英文小写连写、frontmatter 合规、token 不超预算。
4. **保存**：仓库固定目录 `~/Documents/codex-skill-hub/<skill-name>/`（已存在则复用，不重复创建）；需要使用时再安装到 `~/.codex/skills/<skill-name>/`。
5. **版本**：更新 SKILL.md 头部 `**版本**：X.Y（日期）`；在技能文件夹内 `CHANGELOG.md` 按升序追加当前版本与变更内容（旧版本只记录不建目录）。
6. **同步 README**：运行 `scripts/update_readme.py <仓库目录>`，确保 README 技能清单覆盖所有含 SKILL.md 的技能目录且版本与 SKILL.md 一致（幂等，无变化不写文件）。
7. **发布前置检查（Preflight）**：运行 `scripts/preflight_push.sh [仓库目录]`——检测 remote 协议；SSH 先探活 ssh-agent，失败自动尝试回退钥匙 `~/.ssh/neo/neo_git_ed25519`；HTTPS 用 `git push --dry-run` 验证写权限。未通过不进入发布。
8. **发布**：校验门与 Preflight 全绿后执行 git add + commit → 打 tag `<skill-name>@vX.Y` → `git push origin main` + `git push --tags`。
9. **幂等复查**：确认无重复目录、无重复 tag；tag 已存在时用 `git diff <tag> -- <skill-dir>` 对比内容，有差异才做增量提交；输出发布结果（tag 名、提交号、仓库链接）。

## 验收（来自契约）

- SKILL.md 通过官方校验且 name=目录名（英文小写连写）
- 文件夹内 CHANGELOG.md 记录了当前版本与变更
- README 技能清单包含全部含 SKILL.md 的技能目录，版本与 SKILL.md 一致
- 发布前 Preflight 通过；失败时输出可执行的修复指引
- git tag <skill-name>@vX.Y 已推送到 GitHub
- 重复执行不产生重复目录或重复 tag（幂等）

## 失败降级

- 校验认证失败（gh 未登录 / PAT 只读） → 运行 gh auth login 或给 token 授权仓库读取；认证完成前不发布
- 发布认证失败（SSH agent 无身份 / 1Password 未解锁） → 运行 ssh-add 或解锁 1Password SSH agent；preflight 会自动尝试回退钥匙 ~/.ssh/neo/neo_git_ed25519
- 发布认证失败（HTTPS PAT 无写权限） → 给 token 加 Contents: Read and write，或 gh auth login 换 OAuth token
- 技能校验失败 → 按报错修复后重跑校验，禁止放宽规则通过
- 目录或 tag 已存在 → 复用现有目录与 tag，用 git diff <tag> -- <skill-dir> 对比，有差异才增量提交，不重复创建
- README 缺失或清单与技能目录不一致 → 先运行 update_readme.py 修复，禁止跳过 README 直接发布
- 外部依赖缺失（gh / API key） → 读取环境变量或 ~/.config/<skill>/ 配置文件，缺失时明确提示，不静默跳过

## 资源

- scripts/validate_skills.sh：发布前自动校验门（gh skill + skills-ref 双绿，全库扫描）
- scripts/preflight_push.sh：发布前认证/权限检查（remote 协议、SSH agent、回退钥匙、HTTPS 写权限）
- scripts/update_readme.py：README 技能清单同步（发布前必跑，幂等）
- scripts/：确定性逻辑，直接运行
- references/spec.md：技能发布与版本管理规范（与 Obsidian「我的skills」同源）
- references/regressions.md：回归账本（升级前全量回归）

## Token 预算（契约：200 行 / 1800 token）
