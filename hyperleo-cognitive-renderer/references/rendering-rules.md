# 渲染纪律（v0.2）

## Renderer 禁止清单

scripts/render_md.py 及模板层禁止：

- 判断什么更重要（优先级只能读 PIR）
- 改写 / 扩写 summary
- 猜测 risk / action
- 合并 claim
- 创建 recommendation（comparison 的 recommendation 必须来自 view）
- 用当前上下文推断缺失字段

## 确定性保证

相同 PIR + 相同 Profile + 相同 Task View → 完全一致 Markdown。实现约束：

- claim 排序 = 优先级序（critical→important→supporting→technical）+ claim_id 字典序
- 无随机 / 无时间戳注入 / 无外部调用
- 模板占位符用 `safe_substitute`，未知 `$` 原样保留

## Presentation Profile 应用

- `details.technical: collapsed` → 技术字段进 `<details>`
- `numbers.remove_false_precision` → 0–1 的小数按 `percentage_precision` 转百分比
- `style.emoji: restrained` → 只用状态符号（✅ ❌ ⚠️ ⬜ 🟡 ❔）
- 用户偏好只存在于 Profile，禁止写进 PIR

## 噪音清单（Tufte 删除测试）

删除后信息无损的元素 = 噪音：重复状态、无意义小数、过多 Hash、已知上下文、装饰性 Emoji、方法论复述、多余分割线。一次强调 ≤3 处（profile.limits.emphasis_max）。

## 支持视图

decision / diagnosis / comparison / monitor；browse / learning 明确报错（v0.2 未实现）。
