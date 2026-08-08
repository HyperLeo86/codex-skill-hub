---
name: medlit-search
description: 医药/生命科学文献检索与交叉验证（NCBI E-utilities/PubMed + Europe PMC REST API）。Use when the user asks to search medical, biomedical, pharmaceutical, nursing, or life-science literature; retrieve PubMed abstracts or full records by PMID; find a researcher's publications, author positions, or affiliations; verify same-name authors; cross-check results across PubMed and Europe PMC; or produce literature-based research profiles and trend analyses. Requires 1Password on this machine for the NCBI API key (see Secret Handling). 未来可在本 Skill 中扩展其他学科/数据库提供方。
---

# Medlit Search

**版本**：0.1（2026-08-08）

检索医药/生命科学文献，并通过两个独立数据库交叉验证。核心命令都在 `scripts/litsearch.py`，无需额外依赖（仅标准库）。

## 密钥处理（必须遵守）

- NCBI E-utilities 的 API key **不写入本 Skill 任何文件**，运行时按顺序从以下来源解析：
  1. 环境变量 `NCBI_API_KEY`
  2. 1Password：`op read "op://Private/NCBI E-utilities API Key/password"`（通过 `op` CLI 读取，需要桌面端授权）
- 两条规则：**绝不把 key 值写入对话、文件或日志；绝不回显 key**。只在进程环境变量中传递。
- 如果 `op` CLI 不可用或条目不存在：以无 key 模式继续（限 3 次/秒），并在结果中明确提示"未使用 API key"。
- Europe PMC 不需要任何 key。

## 快速开始

```bash
# PubMed 检索（返回 PMID/年份/期刊/标题/作者）
python3 scripts/litsearch.py search pubmed "metformin diabetes" --max 10

# Europe PMC 检索（覆盖更广，含全文与预印本）
python3 scripts/litsearch.py search epmc "metformin diabetes" --max 10

# 按 PMID 取摘要
python3 scripts/litsearch.py abstract 34657320

# 按 PMID 取完整记录（作者位次 + 单位 + 摘要 + DOI），用于身份核验
python3 scripts/litsearch.py fetch 34657320 38093699
```

## 工作流

1. **选库**：
   - 标准 PubMed 检索、PMID 权威记录、跨库链接 → `search pubmed` / `abstract` / `fetch`
   - 查全、全文、预印本、引用/参考文献、宽松标题匹配 → `search epmc`
2. **交叉验证**：同一课题至少跑两个库。典型模式：Europe PMC 宽搜 → PubMed `esummary`/`fetch` 校验 PMID、作者、机构、年份。
3. **作者身份核验（重要）**：中文名/常见英文名同名者很多。用 `fetch` 检查作者位次与 Affiliation，结合合作者名单和主题判断是否为同一人；不确定时标记"待验证"，不要臆断。
4. **检索语法**：PubMed 用 `[Author]`、`[Affiliation]`、`[dp]`、`[Title]`；Europe PMC 用 `AUTH:`、`AFF:`、`TITLE:`、`PUB_YEAR:[a TO b]`。两库语法不通用，详见 `references/databases.md`。
5. **输出**：给出 PMID/DOI、期刊、年份、作者位次与单位、链接；结论标注来源与置信度。

## 参考

- `references/databases.md`：两个库的端点、限流、检索语法、覆盖差异、交叉检索配方。需要处理复杂查询或排错时读取。
- `references/regressions.md`：回归账本，发布/维护后回灌失败模式。

## 扩展性

当前仅覆盖医药/生命科学。未来新增学科/数据库（如工程、机械）时，在 `litsearch.py` 增加对应子命令，并在 `references/` 新增该库的参考文档；SKILL.md 只保留公共工作流。
