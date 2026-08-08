# 数据库参考：NCBI E-utilities 与 Europe PMC REST API

## 1. NCBI E-utilities（PubMed 等 38 个 NCBI 库）

- 基础 URL：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/`
- 常用端点：`esearch.fcgi`（检索）、`esummary.fcgi`（摘要元数据）、`efetch.fcgi`（完整记录）、`elink.fcgi`（跨库链接）、`epost.fcgi`（批量上传）
- 常用参数：`db=pubmed`、`term=`、`retmode=json|xml`、`retmax=`、`sort=pub_date`
- 限流：无 key 3 次/秒；带 key 10 次/秒；超限返回 429。大规模/长期使用需注册 `tool` + `email`。
- 查询语法示例（PubMed 专用）：
  - `Zhao D[Author] AND "Peking University Sixth Hospital"[Affiliation]`
  - `"Anti-Friction MSCs Delivery System"[Title]`
  - `2024:2026[dp]`（日期范围）、`review[pt]`（文献类型）
- 注意：PubMed 标题精确检索对标点/大小写敏感，找不到时改用 Europe PMC 或去掉标点重试。

## 2. Europe PMC REST API

- 基础 URL：`https://www.ebi.ac.uk/europepmc/webservices/rest`
- 常用端点：`/search`、`/fields`、`/{source}/{id}/fullTextXML`、`/{source}/{id}/citations`、`/{source}/{id}/references`
- 无需注册/密钥；约 10 次/秒/IP，超限返回 429
- 覆盖：PubMed 全部摘要 + PMC 全文 + 预印本（bioRxiv/medRxiv 等 34 个服务器）+ 专利/学位论文/Agricola；数据每日同步
- 查询语法示例（Europe PMC 专用，与 PubMed 不通用）：
  - `AUTH:"Danhua Zhao" AND AFF:"Peking University Sixth Hospital"`
  - `TITLE:"DNA hydrogel"`
  - `PUB_YEAR:[2024 TO 2026]`
  - `sort_cited:y`（按引用排序）、`sort_date:y`（按日期排序）
- 结果类型：`idlist` / `lite` / `core`（默认 lite，core 含摘要、MeSH、全文链接）

## 3. 交叉检索配方

1. Europe PMC 宽搜（查全、容错标题）：`search epmc "QUERY"`
2. PubMed 精确核验：`search pubmed "QUERY"` → 对候选 PMID 执行 `fetch`
3. 身份核验：用 `fetch` 检查作者位次、Affiliation、合作者；同名者用"单位 + 核心合作者 + 主题"三重过滤
4. 输出时给出 PMID/DOI、期刊、年份、作者位次与链接

## 4. 常见坑

- 同名作者极多（如 "Yan X"、"Zhao D"、"Yuxuan Diao"），必须核验单位与 ORCID。
- Europe PMC 与 PubMed 命中数不同是正常的：Europe PMC 检索全文，PubMed 只检索摘要/题录。
- 无 PMCID 不代表无全文（可能需订阅）；有 PMCID 可用 Europe PMC `fullTextXML` 拿开放全文。
