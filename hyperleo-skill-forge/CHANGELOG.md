# skill-forge changelog

## 1.5（2026-08-07）

- 重命名：skill-forge → hyperleo-skill-forge（HyperLeo 命名规范，非破坏性重命名）
- 版本 1.4 → 1.5

## 1.4（2026-08-07）

- 重命名：skill-forge → hyperleo-arcane-forge；check_skill.py / build_skill.py 强制执行 HyperLeo 命名规范（hyperleo- 前缀 + 2–3 词）
- 触发面：description 明确触发句补足 7 条（≥6），移除「任何涉及…自动触发」元叙述
- 反触发：新增「发布/打 tag/同步到 GitHub（走 skill-publisher）」，与 publisher 分界
- 铁律 7：大模型版本升级后全量回归账本场景 + 旧补丁可删性检查
- 来源：skill-analyst 1.0.0 四维体检（P2-U1 / P2-M3 / P2-E4）

## 1.3（2026-08-03）

- 原 1-1 / 1-2 / 1-3 三个版本目录合并为单一 skill-forge 目录，只保留最新版（幂等）
- 相对 1.2 的六项升级：
  1. 契约校验化：触发句下限统一为 ≥6，check 新增 spec 必填字段校验
  2. 账本种子：build_skill.py 自动生成 references/regressions.md，check 校验存在性
  3. 决定权条款：生成器按 freedom 输出「该锁死/该留白」条款
  4. description 升级：第三人称能力描述 + 触发句直接罗列 + 反触发
  5. 版本纪律：SKILL.md 头部一行版本 + 日期；变更记录放本文件夹 CHANGELOG.md
  6. 检查强化：name=目录同名、folded description 解析、references 一层深、脚本可执行位、账本存在性

## 1.2（2026-08-03）

- 契约闭环五步：压缩 → 生成 → 验证 → 回灌 → 固化
- 一页契约模板、token 预算表、A/B 前向测试协议、失败模式账本
- 注：该版本曾被另一会话原地升级丢失，后从 outputs 备份完整恢复，恢复记录保留在 git 历史与上文

## 1.1（2026-08-03）

- 官方 Skill Creator 常规升级版：意图捕获卡、token 硬预算、验证门、TDD 式前向测试
