# 领域参考（按任务类型加载，保持上下文精简）

## dev（代码/库/API/基础设施）

- 先读 `requirements.txt` / `pyproject.toml` / `package.json` / `go.mod`，尊重既有栈
- 找库：npm / PyPI / crates.io + GitHub topics（`stars:>500`）
- 找替代：openalternative.co、awesome-selfhosted、alternativeto.net（过滤 Open Source）
- 安全：新依赖建议跑 `pip-audit` / `npm audit`
- 评价：Reddit r/python、HN（hn.algolia.com）、GitHub Discussions

## writing（文档/模板/内容）

- 找模板：Notion 模板市场、Canva、Google Workspace 模板库、GitHub awesome-* 列表
- 找框架：写作框架 / SOP 模板 / 报告模板
- 注意：GitHub stars 对非开发任务的权重降低

## data（数据/分析/ML）

- 找数据集：Hugging Face、Kaggle、Papers with Code Datasets、Zenodo、政府开放数据
- 找方法：arXiv、Papers with Code、Semantic Scholar
- 评估：许可（ODC / CC）、更新频率、规模与格式

## ops（运维/CI/CD/流程）

- 找基础设施：GitHub Actions marketplace、Terraform Registry、Helm Hub
- 找服务：free-for.dev、云厂商免费额度、自托管清单
- 评估：维护方数量、Docker/Helm 支持、数据可移植性

## 领域适配原则

- 已有栈的优先沿用；换方案必须给出明显收益
- 商品化能力（用户不关心谁做的）→ 用现成；核心能力才考虑自建
