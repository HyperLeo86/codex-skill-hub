# Leo's Codex-Skills

个人 Codex 技能集合与版本管理仓库（私有）。

## 技能清单

| 技能 | 版本 | 说明 |
| --- | --- | --- |
| fan-shi-yue-qian | 1.0.0 | 范式跃迁：解题前换坐标系，寻找数量级提升的解法 |
| jian-suo-shi-jie | 1.3.0 | 检索世界：先找世界上已有的现成方案，避免重复造轮子 |
| jian-suo-shi-jie-pro | 1.4.0 | 检索世界 Pro：查询变体扩展 + 多路合并重排 + 历史库回灌 + 检索日志 |
| skill-forge-1-1 | 1.1.0 | 打造技能：官方 Skill Creator 常规升级版 |
| skill-forge-1-2 | 1.2.0 | 打造技能：契约驱动 + 可测试 + 自进化（范式跃迁版，已恢复） |
| skill-forge-1-3 | 1.3.0 | 打造技能：契约校验化 + 决定权条款 + 账本种子 + 发布门 |

## 版本管理规则

- 版本号采用 SemVer（主版本.次版本.补丁）
- 每个技能用 tag `技能名@vX.Y.Z` 标记版本，例如 `skill-forge-1-3@v1.3.0`
- 所有版本变更记录在根目录 `CHANGELOG.md`；skill 文件夹内不放置 README / CHANGELOG 等人类文档（遵守 skill-forge 的版本纪律）
- 初始入库日期：2026-08-03

## 本地安装

把对应技能目录复制到 `~/.codex/skills/` 下即可：

```bash
cp -R skill-forge-1-3 ~/.codex/skills/
```

## 说明

- 检索类脚本所需的 API key（Exa / Tavily）不随仓库分发，从环境变量或 `~/.config/jian-suo-shi-jie/*.env` 读取
- skill-forge 系列当前保留 1-1 / 1-2 / 1-3 三个版本目录（1-2 为恢复副本）；后续优化轮可评估合并为单一 `skill-forge` 目录 + tag 管理
- 当前为私有仓库；如后续要公开，需要先补充 LICENSE
