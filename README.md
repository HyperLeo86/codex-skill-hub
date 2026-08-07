# codex-skill-hub

个人 Codex 技能集合与版本管理仓库（私有）。每个技能只保留一个最新版本目录，版本历史记录在各自文件夹的 CHANGELOG.md。

## 技能清单

| 技能 | 版本 | 说明 |
| --- | --- | --- |
| codex-1password-secrets | 1.3 | 审计并落地 Codex × 1Password 统一密钥管理；本地 ~/.codex/.env 只作纯 KEY=VALUE 显式缓存，按需 pull/push 同步 |
| image-gen-router | 1.0 | 统一路由并调用用户已开通的生图 API（阿里通义万相 DashScope、火山方舟 ARK），按可用 Key 与任务类型自动选择模型，未来新增提供方只需扩展注册表 |
| paradigm-leap | 1.1 | 在解题之前先换坐标系：压缩问题、测量基线、扫描世界、抽象机制、跨域迁移、最小验证、固化进化，寻找数量级提升的解法（降维打击） |
| prd-writer | 1.0 | 示例驱动的可执行 PRD（产品需求文档）撰写与审核技能：三视角访谈 → 概念版对齐 → 落地版（每条规则配例子、AC 产出 GWT）→ DoR 100 分闸门 → 纵横审核 → 交… |
| skill-forge | 1.4 | 用「契约驱动 + 可测试 + 自进化」创建或升级 Agent 技能（Skill），统一版 v1.4：契约校验化、决定权条款、账本种子与发布门 |
| skill-publisher | 1.3 | 按「技能发布与版本管理规范」生成、校验 Codex 技能，维护版本与 CHANGELOG，并发布到 GitHub |
| world-search-pro | 1.1 | 动手前的方案侦察 + 决策 + 归档完整流水线：多引擎检索、六层选型、业务价值与许可硬检查、谱系解释、Verdict 行与置信度、报告归档 |

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
