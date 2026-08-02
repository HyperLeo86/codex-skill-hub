---
name: skill-forge-1-1
description: >-
  创建或升级可复用的 Agent 技能（Skill），是官方 Skill Creator 的 v1.1.0 常规升级版。核心升级：意图捕获卡、token 硬预算、验证门与 TDD 式前向测试。当用户要求「打造/创建/升级一个技能」「写 SKILL.md」「把某个重复流程做成 Codex 技能」「用 1.1 / 常规升级版打造技能」时使用。不用于插件清单修改、MCP 配置等非技能任务。
---

# 打造技能 v1.1.0

**版本**：1.1.0（2026-08-03）

## 定位

在官方 skill-creator 流程（理解 → 规划 → 初始化 → 编辑 → 验证 → 迭代）之上加入三道升级：

1. **意图捕获卡**：用最少问题锁定触发场景、验收标准与反触发
2. **Token 硬预算**：SKILL.md 与引用文件全部计量，超预算即拆分
3. **验证门**：结构校验 + token/链接检查 + TDD 式前向测试

## 工作流

### 1. 意图捕获（最多问 3 个问题）

默认假设（不询问，除非用户明确冲突）：
- 安装位置：`~/.codex/skills/`（`CODEX_HOME` 未设时）
- 语言：跟随用户当前对话语言
- 技能名：动词开头、小写连字符，如 `weekly-report-writer`

只问会影响成败的问题，最多 3 个，优先顺序：
1. 触发场景：用户说什么话、在什么场景应调用它？（用户没想法时，主动给 3 个候选触发句）
2. 输入输出：输入什么、产出什么、验收标准是什么？
3. 边界：明确不该做什么，防止误触发与范围膨胀。

产出**意图卡**（≤6 行）：

```text
技能名 / 一句话定位
触发句：≥3 个真实用户说法
输入 → 输出：…
验收标准：可观察、可检查
反触发：…
```

### 2. 复用优先（5 分钟）

动手前先查：
- 本机已有：`~/.codex/skills/`、`~/.codex/plugins/`，避免重复造轮子
- 全球生态：agentskills.io、awesome-agent-skills、obra/superpowers

决策顺序：直接用 > 改改用 > 借鉴再自建 > 从零自建。自建时必须能说清「现成方案差在哪里」。

### 3. 精益设计（Token 硬预算）

| 文件 | 预算 | 超标处理 |
| --- | --- | --- |
| SKILL.md | ≤300 行 / ≤2500 token | 拆到 references/，正文留路由 |
| description | ≤100 词 | 只保留触发词与任务词 |
| references/* | 按需加载；单文件 ≤10k 词 | 加目录 + grep 提示 |
| scripts/* | 执行时不必读进上下文 | 直接运行，不写进正文 |

按任务脆弱度设定自由度：
- **低自由度**（操作脆弱、顺序固定）→ 明确步骤或脚本
- **中自由度**（有偏好模式）→ 伪代码/带参数脚本
- **高自由度**（开放任务）→ 原则 + 简洁范例

### 4. 实现

1. 用官方脚手架初始化：
   `python3 /Users/leo/.codex/skills/.system/skill-creator/scripts/init_skill.py <name> --path <dir> --resources scripts,references --interface display_name=... --interface short_description=... --interface default_prompt=...`
2. 只保留实际需要的资源目录，删除模板占位文件
3. SKILL.md 正文用祈使句；只写「模型不知道或容易做错」的程序性知识
4. 大而稳定的逻辑放 scripts/；细节放 references/；输出模板放 assets/

### 5. 验证门（强制，不可跳过）

1. 结构校验：运行官方 `quick_validate.py <skill-dir>`，失败先修复
2. 质量检查：运行本技能 `scripts/check_skill.py <skill-dir>`，清零所有 ERROR，处理 WARN
3. 触发测试：用意图卡的 3 个触发句模拟调用，确认 description 能命中
4. 前向测试（TDD 红绿循环，见 references/validation.md）：
   - RED：不带技能，让独立 subagent 跑 1 个真实任务，记录失败
   - GREEN：带技能重跑同一任务，确认行为改变
   - REFACTOR：堵漏洞；显式反驳常见借口（如「我稍后补测试」）
5. 修复循环最多 3 轮；仍不过则交付时写明「已知边界」

### 6. 交付与进化

交付摘要包含：路径、触发示例、验收结果、已知边界、建议版本号。

升级规则：修复 = patch；加能力 = minor；破坏触发或结构 = major。
真实使用后若出现失败模式，记入 `references/regressions.md`（若该技能有），下次创建前自动查重。

## 质量评分（交付前自评 1–5）

| 维度 | 检查问题 |
| --- | --- |
| 触发准确 | description 含触发场景与反触发？误触发风险低？ |
| Token 成本 | SKILL.md 在预算内？references 按需加载？ |
| 工作流可靠 | 步骤可重复？脚本确定性？失败时有降级路径？ |
| 产物质量 | 真实任务输出满足验收标准？ |
| 泛化性 | 换措辞、换输入仍能用，而非只对样例有效？ |

评分 <4 的维度必须写明改进方案或已知边界。

## 资源

- `scripts/check_skill.py`：结构、token、链接、孤儿文件检查（用法见文件头）
- `references/validation.md`：TDD 前向测试协议与反合理化清单

## 铁律

1. 不创建 README.md / CHANGELOG.md / INSTALLATION_GUIDE.md 等人类文档
2. description 之外不写「何时使用」章节
3. 任何一步卡住超过 2 轮，停止并汇报，不硬编造结果
