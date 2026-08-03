# codex-skill-hub

个人 Codex 技能集合与版本管理仓库（私有）。每个技能只保留一个最新版本目录，版本历史记录在各自文件夹的 CHANGELOG.md。

## 技能清单

| 技能 | 版本 | 说明 |
| --- | --- | --- |
| paradigm-leap | 1.0 | 范式跃迁：解题前换坐标系，寻找数量级提升的解法 |
| world-search | 1.4 | 检索世界：先找世界上已有的现成方案，避免重复造轮子（统一版，原 Pro 能力已并入） |
| skill-forge | 1.3 | 打造技能：契约驱动 + 可测试 + 自进化（1-1 / 1-2 / 1-3 统一为最新版） |
| skill-publisher | 1.1 | 发布管理：按规范生成、自动校验（gh skill + skills-ref）、版本化并发布到 GitHub |

## 版本管理规则

- 每类技能只保留一个最新版本目录（幂等），同一项目只有一个文件夹
- 版本号按 1.1、1.2 式排序；历史变更记录在对应文件夹的 `CHANGELOG.md`
- 每个技能用 tag `技能名@vX.Y` 标记当前版本，例如 `skill-forge@v1.3`
- 旧版本不另建目录，由 git 提交历史保留
- 初始入库日期：2026-08-03

## 本地安装

把对应技能目录复制到 `~/.codex/skills/` 下即可：

```bash
cp -R skill-forge ~/.codex/skills/
```

## 说明

- 检索类脚本所需的 API key（Exa / Tavily）不随仓库分发，从环境变量或 `~/.config/world-search/*.env` 读取（兼容旧路径 `~/.config/jian-suo-shi-jie/`）
- 当前为私有仓库；如后续要公开，需要先补充 LICENSE
