---
name: skill-publisher
description: 按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub。当用户说 「把 xxx 做成一个 skill」；「生成一个新技能并发布到 GitHub」；「发布这个 skill」；「按规范创建技能并打版本 tag」；「更新技能版本并推送」；「帮我写技能规范并做成 skill」；「把本地技能同步到 codex-skill-hub」 时使用；不用于：市场调研或竞品分析、修改 MCP 服务器或插件清单、只写说明文档不创建技能。
---

# skill-publisher

**版本**：1.1（2026-08-03）

## 概览

按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub

## 触发与反触发

- 触发：把 xxx 做成一个 skill；生成一个新技能并发布到 GitHub；发布这个 skill；按规范创建技能并打版本 tag；更新技能版本并推送；帮我写技能规范并做成 skill；把本地技能同步到 codex-skill-hub
- 反触发：市场调研或竞品分析；修改 MCP 服务器或插件清单；只写说明文档不创建技能

## 决定权（自由度 medium）

- 按伪代码/模板执行，参数可依上下文调整
- 输出格式遵循模板，内容允许合理变化

## 工作流

1. **输入处理**：确认是新技能还是更新已有技能；先读 `references/spec.md`（规范）与 `references/regressions.md`（账本），命中已知失败模式必须写防复发条款。
2. **生成/更新**：新技能先写一页契约 `spec.json`（triggers ≥6、anti_triggers ≥1、acceptance ≥3、failure_modes ≥3、token_budget），再按契约生成 SKILL.md 骨架并填充程序性知识；已有技能直接定位目录做增量修改。
3. **校验（自动门）**：先运行 `scripts/validate_skills.sh`——内置 `gh skill publish --fix`（GitHub 官方 agentskills 校验 + 安全检查）与 `skills-ref validate`（全库逐技能校验）双保险，全绿才允许继续；再运行 `check_skill.py <dir> [spec.json]` 做结构/token/账本检查，要求 name=目录名、英文小写连写、frontmatter 合规、token 不超预算。
4. **保存**：仓库固定目录 `~/Documents/codex-skill-hub/<skill-name>/`（已存在则复用，不重复创建）；需要使用时再安装到 `~/.codex/skills/<skill-name>/`。
5. **版本**：更新 SKILL.md 头部 `**版本**：X.Y（日期）`；在技能文件夹内 `CHANGELOG.md` 按升序追加当前版本与变更内容（旧版本只记录不建目录）。
6. **发布**：校验门全绿后执行 git add + commit → 打 tag `<skill-name>@vX.Y` → `git push origin main` + `git push --tags`。
7. **幂等复查**：确认无重复目录、无重复 tag；tag 已存在时对比内容只做增量提交；输出发布结果（tag 名、提交号、仓库链接）。

## 验收（来自契约）

- SKILL.md 通过官方校验且 name=目录名（英文小写连写）
- 文件夹内 CHANGELOG.md 记录了当前版本与变更
- git tag <skill-name>@vX.Y 已推送到 GitHub
- 重复执行不产生重复目录或重复 tag（幂等）

## 失败降级

- gh 未登录或权限不足 → 提示先运行 gh auth login，认证完成前不发布
- 技能校验失败 → 按报错修复后重跑校验，禁止放宽规则通过
- 目录或 tag 已存在 → 复用现有目录与 tag，对比内容差异后只做增量提交，不重复创建
- 外部依赖缺失（gh / API key） → 读取环境变量或 ~/.config/<skill>/ 配置文件，缺失时明确提示，不静默跳过

## 资源

- scripts/validate_skills.sh：发布前自动校验门（gh skill + skills-ref 双绿，全库扫描）
- scripts/：确定性逻辑，直接运行
- references/spec.md：技能发布与版本管理规范（与 Obsidian「我的skills」同源）
- references/regressions.md：回归账本（升级前全量回归）

## Token 预算（契约：200 行 / 1800 token）
