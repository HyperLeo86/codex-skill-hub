# 技能发布与版本管理规范（Codex Skills）

> 状态：v1.3 · 2026-08-07 更新 · 适用仓库：`codex-skill-hub`（public，2026-08-07 确认）
> 依据：agentskills.io 开放规范、GitHub CLI `gh skill` 官方工具、OpenAI Codex 官方文档，以及个人实践。

## 1. 总则

1. **一个技能 = 一个文件夹**：同一技能只保留一个最新版本目录，不按版本建多个目录（幂等）。
2. **旧版本由 git 提交历史保留**：不在工作区保留旧版本目录，旧版本记录进对应文件夹的 `CHANGELOG.md`。
3. **版本说明在文件夹内**：每个技能文件夹自带 `CHANGELOG.md`，版本号 + 修改内容都记录在那里。
4. **可自动化、可校验**：所有流程必须能被命令行重复执行；同一输入重复执行结果一致（不产生重复目录 / 重复 tag）。
5. **规范文档唯一来源**：本文件是技能的“宪法”；技能实现与本文件冲突时，以本文件为准。

## 2. 命名规范

1. 文件夹名 = `name` 字段 = **英文小写连写（kebab-case）**：只含小写字母、数字、连字符，不以连字符开头/结尾，≤64 字符。
2. **禁止拼音连写**（如 `fan-shi-yue-qian`），**禁止把版本号写进名字**（如 `skill-forge-1-3`）。
3. 中文触发词放 `description`，不放名字；展示名（display_name）可用英文单词（如 `Paradigm Leap`）。

| 正例 | 反例 |
| --- | --- |
| `skill-publisher` | `skill-publisher-1-0` |
| `world-search` | `jian-suo-shi-jie` |
| `paradigm-leap` | `fan-shi-yue-qian` |

## 3. 文件结构规范

```text
skill-name/
├── SKILL.md              # 必填：frontmatter + 正文
├── CHANGELOG.md          # 必填：本技能版本记录（唯一变更记录）
├── agents/openai.yaml    # 可选：Codex 专属界面/默认提示词
├── references/*.md       # 可选：按需加载的参考文档（一层深）
├── scripts/*             # 可选：自包含脚本
└── assets/               # 可选：模板/静态资源
```

### SKILL.md frontmatter（遵循 agentskills.io）

| 字段 | 必填 | 约束 |
| --- | --- | --- |
| `name` | 是 | 与父目录同名；小写字母/数字/连字符 |
| `description` | 是 | ≤1024 字符；说明“做什么 + 何时用”，含触发词与反触发 |
| `license` | 否 | 许可证名或文件 |
| `compatibility` | 否 | 环境要求 |
| `metadata` | 否 | 任意键值（可放版本等） |
| `allowed-tools` | 否 | 预授权工具（实验性） |

### 正文要求

- 结构：定位 → 工作流 → 验收 → 失败降级 → 资源
- SKILL.md 全文件 ≤300 行 / ≤2500 token；细节拆到 `references/`
- references 一层深，按需加载；脚本自包含、报错信息可读

## 4. 生成规范（契约驱动）

写正文之前先写一页契约（`spec.json`）：

- `triggers` ≥6 条真实触发句
- `anti_triggers` ≥1 条反触发
- `acceptance` ≥3 条可自动检查的验收
- `failure_modes` ≥3 条，每条有降级路径
- `token_budget` 必填（SKILL.md 行数 / token 数）

生成后用官方校验器检查：`quick_validate.py` 或 agentskills 的 `skills-ref validate`；再用 `check_skill.py` 做结构/token/spec/账本检查。

**发布门三绿**：check 全绿 + 回归账本全绿 + A/B 或 RED→GREEN 测试达标。三绿不满足不发布。

## 5. 保存规范

- 本地安装目录：`~/.codex/skills/<skill-name>/`
- 仓库目录：`~/Documents/codex-skill-hub/<skill-name>/`（与 GitHub 同名同步）
- 规范文档：本文件存 Obsidian「我的skills」，改动后必须同步给技能与仓库

## 6. 版本管理规范

1. 版本号用 `1.1`、`1.2` 式（major.minor）；破坏性变更升 major。
2. SKILL.md 正文头部写一行：`**版本**：X.Y（YYYY-MM-DD）`。
3. 每个技能文件夹内 `CHANGELOG.md`，按版本**升序**记录：`## 1.1` → `## 1.2`，每条注明日期与变更内容；旧版本不建目录。
4. git tag 格式：`<skill-name>@vX.Y`（如 `skill-publisher@v1.2`），tag 推送到 GitHub。
5. 升级流程：改内容 → 更新版本行 + CHANGELOG → 同步 README 技能清单 → 校验 → Preflight（认证/权限检查）→ commit → tag → push。
6. 幂等：目录已存在则复用；tag 已存在则对比内容，不重复创建。

## 7. 发布规范（GitHub）

1. 仓库：`codex-skill-hub`，public，`main` 分支。
2. 校验（自动门）：发布前必须运行 `skill-publisher/scripts/validate_skills.sh`——内置 `gh skill publish --fix`（官方 agentskills 规范 + 安全检查）与 `skills-ref validate`（全库逐技能）双校验，双绿后运行 `skill-publisher/scripts/preflight_push.sh` 确认发布认证可用，再 `git push --tags`。
3. 推荐开启：tag protection、secret scanning、code scanning；公开分享时开启 immutable releases。
4. 敏感信息：API key 一律环境变量或 `~/.config/<skill-name>/*.env`，禁止入库。
5. **README 同步**：每次发布/更新技能后必须运行 `skill-publisher/scripts/update_readme.py <仓库目录>` 更新 README 技能清单（技能名 / 版本 / 说明），清单须与全部含 SKILL.md 的技能目录一致；幂等，无变化不产生提交。

## 8. 参考来源

- [Agent Skills 规范](https://agentskills.io/specification)（agentskills/agentskills，Apache-2.0）
- [gh skill：用 GitHub CLI 管理 agent skills](https://github.blog/changelog/2026-04-16-manage-agent-skills-with-github-cli/)
- [OpenAI Codex Skills 文档](https://developers.openai.com/codex/skills)
- [anthropics/skills 官方示例库](https://github.com/anthropics/skills)
- 同类项目参考：qiaomu-skill-publisher、skilldock、motiful/skill-forge（详见检索世界方案卡）

## 9. 待办

- ✅ 已完成：gh skill publish --fix + skills-ref validate 已内嵌为 skill-publisher 1.1 的自动校验门
- ✅ 已完成：v1.2 内嵌 README 技能清单同步（update_readme.py）
- 公开仓库：为每个技能补 license 字段（推荐，进行中）
- 本地旧版本目录清理（skill-forge-1-1/1-2/1-3、jian-suo-shi-jie-pro；现已有备份，可随时删除）
