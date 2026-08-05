# 渠道矩阵与六层选型

## 渠道（按需求类型选择，至少 2–3 层）

1. 通用搜索：Exa（主引擎）、Tavily（交叉验证）、内置搜索
2. 代码与库：GitHub Topics / Search、awesome-*、npm / PyPI / crates.io
3. 产品与工具：AlternativeTo、openalternative.co、Product Hunt、AI 工具导航
4. 服务与 API：云厂商市场、RapidAPI、Smithery / Glama / mcp.so
5. 学术与方法：arXiv、Papers with Code、Semantic Scholar
6. 数据与数据集：Hugging Face、Kaggle、Zenodo
7. 内容与知识：官方文档、YouTube / B 站 / 知乎 / Dev.to
8. 社区评价：Reddit、HN、GitHub Issues / Discussions、V2EX
9. 智能体生态：MCP 目录、skill/plugin 市场、官方 Cookbook
10. 历史库：~/Documents/solution-scout-history（先查自己）

## 六层选型顺序（每层无候选再进下一层，逐层留引用）

| 层 | 含义 | 判据 |
|---|---|---|
| REUSE | 仓库/组织内已有 | rg / 已有依赖 |
| USE | 维护中的包/服务直接可用 | 功能匹配 + 许可宽松 + 活跃 |
| FORK | 需要复制/vendor/补丁 | 检查 stars/贡献者/发布频率/许可 |
| BUY | SaaS 产品解决 | TCO 与隐私可接受 |
| INTEGRATE | API 解决 | 调用即可，不持有运维面 |
| BUILD | 自建 | 前面全无候选 + 自建理由 |

## 评估硬规则

- 每个候选必须能指回真实来源；禁止编造
- 成熟度 L3+ 必须 ≥2 个独立来源
- AGPL / GPL / BSL / 商业双许可必须显式写出合规后果（内部工具 vs 对外分发）
- 反偏见：≥3 个独立来源交叉验证；警惕「Top 10 博客把自家产品排第一」
- 查废弃：archived / 12 个月无提交且关键 issue 未处理 → 淘汰
- 查成本：license、pricing、self-hosted 是否有
- 社区真实度：Reddit / HN / Issues 的负面评价比官方宣传可信

## 搜索技巧

- 反搜：`X alternative`、`X vs Y`、`X reddit`、`X 坑`
- 逆向翻译：中文功能描述 → 英文动词短语（如「表格转网页」→ spreadsheet to dashboard）
- 找合集：awesome-*、50+ tools、工具导航
- 顺藤摸瓜：README 的 Alternatives / Related 常带同类
