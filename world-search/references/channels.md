# 渠道目录（搜索目录）

## 使用方式

- 按需求类型选择层级；每层至少打 2–3 个渠道。
- 每个候选只记：名称、链接、一句话、来源、日期。
- 中英文搜索词各一套；中文渠道至少占三分之一。
- 发现与评估分离：扫描阶段不判断好坏。
- 第 1 层先用 Exa 跑语义查询（`scripts/exa_search.py`，主引擎），再用关键词引擎与渠道矩阵叠加（Codex 内置搜索）。
- 候选确认阶段用 Tavily 交叉验证（`scripts/tavily_search.py`，第二引擎），再回到渠道矩阵确认一手来源。

## 十层渠道

| 层 | 渠道 | 适合找 |
| --- | --- | --- |
| 1. 通用搜索 | **Exa（语义检索 API，主引擎）**；**Tavily（结构化交叉验证，第二引擎）**；Google、Bing、百度、夸克（用 site: 语法） | 全局线索、概念型查询、候选验证 |
| 2. 代码与库 | GitHub Search / Topics / awesome 列表；GitLab；npm、PyPI、crates.io、Homebrew、Maven | 开源库、源码、示例 |
| 3. 产品与工具 | Product Hunt、AlternativeTo、G2、App Store、少数派、AI 工具导航站 | 成熟产品或工具 |
| 4. 服务与 API | 云厂商市场、RapidAPI、API 目录、MCP 目录（Smithery、mcp.so、Glama）、插件/技能市场 | API、托管服务、技能 |
| 5. 学术与方法 | arXiv、Google Scholar、Papers with Code、Semantic Scholar、OpenReview | 算法、方法、论文 |
| 6. 数据与数据集 | Hugging Face、Kaggle、Zenodo、Papers with Code Datasets、政府开放数据 | 数据集、模型 |
| 7. 内容与知识 | YouTube、B站、知乎、小红书、Medium、Dev.to、官方文档、awesome 教程列表 | 教程、技能、「怎么做」 |
| 8. 社区评价 | Reddit、Hacker News、V2EX、X、即刻、Discord/Slack、GitHub Issues/Discussions | 真实评价、已知坑 |
| 9. 智能体生态 | Agent 框架文档（LangChain、LlamaIndex、AutoGen、CrewAI、Microsoft Agent Framework）、MCP 目录、OpenAI/Anthropic 官方示例与 Cookbook、GitHub awesome-* 列表、skill/plugin 市场 | agent 相关方案、技能 |
| 10. 历史库 | `~/Documents/solution-scout-history` 的 index.html | 同类需求先查自己 |

## 搜索技巧

- **反搜**："X alternative"、"X 替代"、"没有 X 怎么 Y"、"X reddit"、"X 知乎"
- **逆向翻译**：把中文功能描述翻成英文动词短语，如「表格变网页」→ "spreadsheet to dashboard"、"data to webpage"
- **找合集**：awesome-* 列表、「50+ tools」类文章、工具导航站
- **查废弃**：GitHub archived、last commit、discontinued、unmaintained
- **查成本**：license、pricing、self-hosted 是否有
- **顺藤摸瓜**：优秀项目的 README 里常带 Alternatives / Related / 对比表，顺着找同类
- **交叉验证**：一个方案至少有两个独立来源提到，才可判「成熟」
- **深度确认**：判断「能不能用」看文档和 Issues；判断「好不好用」看社区抱怨

## 来源可信度

- 一手来源：官网、GitHub、论文原文、官方文档——用于确认事实
- 二手来源：博客、榜单、评测——只用于发现线索，不用于结论
- 社区真实度：Reddit / HN / V2EX / 知乎的抱怨与负面评价，比官方宣传更可信
- 找不到负面评价时，主动搜 "X problems"、"X issues"、"X 坑"
