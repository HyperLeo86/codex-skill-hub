#!/usr/bin/env python3
"""Deterministically render audit-result.json into an Obsidian human report.

The human report is a deterministic projection of the canonical result:
- fixed structure: status -> problems -> actions -> technical evidence
- no new facts, no second audit, no LLM reinterpretation
- hashes and machine internals sink to metadata / collapsed details
Machine schema stays English; --locale controls the human language (default zh-CN).
"""
import argparse
import sys
from pathlib import Path

from common import canonical_json, read_json

MATURITY_ZH = {"L1": "原型", "L2": "结构化", "L3": "可测试", "L4": "治理级", "L5": "认证级"}
CERT_ZH = {"C0": "未审计", "C1": "已收集证据", "C2": "已完成语义验证", "C3": "已通过复现验证", "C4": "生产级认证"}
STATUS_ZH = {
    "CERTIFIED": "✅ 已认证",
    "INSUFFICIENT_EVIDENCE": "⚠️ 证据不足",
    "UNSTABLE": "⚠️ 结果不稳定",
    "INVALID_INPUT": "❌ 输入无效",
    "HUMAN_ADJUDICATED": "人工裁决",
}
LIFECYCLE_ZH = {"KEEP": "保持", "UPGRADE": "升级", "MERGE": "合并", "SPLIT": "拆分", "DEPRECATE": "弃用"}
PROVISIONAL_ZH = {
    "KEEP_CANDIDATE": "KEEP 候选",
    "UPGRADE_CANDIDATE": "UPGRADE 候选",
    "MERGE_CANDIDATE": "MERGE 候选",
    "SPLIT_CANDIDATE": "SPLIT 候选",
    "DEPRECATE_CANDIDATE": "DEPRECATE 候选",
    "NONE": "暂无明确方向",
    None: "暂无明确方向",
}
FINDING_EMOJI = {"healthy": "✅", "concern": "⚠️", "failure": "❌", "unknown": "❔"}
FINDING_ZH = {"healthy": "通过", "concern": "有缺口", "failure": "存在问题", "unknown": "未知"}
FINDING_KEYS = [
    ("Identity", "Identity 身份"),
    ("Necessity", "Necessity 必要性"),
    ("Integrity", "Integrity 完整性"),
    ("Purity", "Purity 纯粹性"),
    ("Boundary", "Boundary 边界"),
    ("Position", "Position 生态位"),
    ("Behavior", "Behavior 行为"),
]
COVERAGE_ROWS = [
    ("Skill 快照", "snapshot_coverage"),
    ("决策证据", "decision_evidence_coverage"),
    ("行为测试", "behavior_coverage"),
    ("Usage 数据", "usage_coverage"),
    ("独立复现", "reproducibility_coverage"),
]


def pct(value):
    if value is None:
        return "N/A"
    return f"{round(value * 100)}%"


def fmt_level(value) -> str:
    if isinstance(value, dict):
        return f"{value.get('level', '')} {value.get('name', '')}".strip()
    return str(value)


def quality_phrase(health) -> str:
    if health is None:
        return "状态未评估"
    if health >= 90:
        return "整体健康"
    if health >= 70:
        return "整体良好"
    if health >= 50:
        return "存在明显问题"
    return "问题严重"


def build_summary(result: dict) -> str:
    health = result.get("health_score")
    maturity = result.get("maturity_level") or {}
    m_level = maturity.get("level", "")
    maturity_short = MATURITY_ZH.get(maturity.get("level"), "")
    cert = result.get("certification_level") or {}
    cl = cert.get("level")
    if cl == "C4":
        cert_phrase = "已完成正式认证"
    elif cl in ("C2", "C3"):
        cert_phrase = "部分完成认证"
    else:
        cert_phrase = "暂未完成正式认证"
    gaps = [b.get("gap", "") for b in result.get("blockers", []) if b.get("gap")]
    stage = f"{m_level} · {maturity_short}" if m_level else maturity_short
    parts = [f"{quality_phrase(health)}，已达到 {stage}；{cert_phrase}。"]
    if gaps:
        parts.append(f"主要缺口：{'、'.join(gaps[:2])}。")
    return " ".join(parts)


def render_zh(result: dict) -> str:
    lines = []
    lines.append(f"# 🧩 Skill Audit · `{result.get('target_skill', 'unknown')}`")
    lines.append("")
    lines.append(f"> **当前判断：** {build_summary(result)}")
    lines.append("")

    lines.append("## 核心状态")
    lines.append("")
    lines.append("| 指标 | 状态 | 说明 |")
    lines.append("| --- | ---: | --- |")
    health_status = result.get("health_score_status", "PARTIAL")
    health_label = "已验证健康度" if health_status == "VERIFIED" else "暂定健康度"
    health_note = {
        "VERIFIED": "已验证质量项全部通过",
        "PARTIAL": "结构检查全过，关键证据未齐",
        "PROVISIONAL": "存在未通过检查项",
    }.get(health_status, "关键证据未齐")
    lines.append(f"| **{health_label}** | **{result.get('health_score')} / 100** | {health_note} |")
    metrics = result.get("metrics", {})
    decision_cov = metrics.get("decision_evidence_coverage")
    decision_note = "缺少真实 usage 证据" if metrics.get("usage_coverage", 0) == 0 else "决策关键字段已覆盖"
    lines.append(f"| **证据完整度** | **{pct(decision_cov)}** | {decision_note} |")
    maturity = result.get("maturity_level") or {}
    m_level = maturity.get("level", "")
    maturity_note = {
        "L1": "原型阶段",
        "L2": "已结构化",
        "L3": "已具备可执行测试",
        "L4": "已达到完整治理阶段",
        "L5": "已通过正式认证",
    }.get(m_level, "")
    lines.append(f"| **成熟度** | **{m_level} · {MATURITY_ZH.get(m_level, m_level)}** | {maturity_note} |")
    cert = result.get("certification_level") or {}
    c_level = cert.get("level", "")
    cert_note = {
        "C0": "尚未收集证据",
        "C1": "尚未通过独立复现认证",
        "C2": "已通过语义验证",
        "C3": "已通过复现验证",
        "C4": "已认证",
    }.get(c_level, "")
    lines.append(f"| **认证等级** | **{c_level} · {CERT_ZH.get(c_level, c_level)}** | {cert_note} |")
    decision = result.get("lifecycle_decision")
    if decision is None:
        lifecycle_cell, lifecycle_note = "⏸ 暂缓裁决", "关键证据不足"
    else:
        lifecycle_cell = f"{decision} · {LIFECYCLE_ZH.get(decision, decision)}"
        lifecycle_note = "正式裁决已发布"
    lines.append(f"| **生命周期** | **{lifecycle_cell}** | {lifecycle_note} |")
    lines.append("")

    lines.append("## 能力审计")
    lines.append("")
    lines.append("| 维度 | 状态 | 关键判断 |")
    lines.append("| --- | :-: | --- |")
    findings = result.get("findings", {})
    for key, zh in FINDING_KEYS:
        item = findings.get(key, {})
        status = str(item.get("status", "unknown")).lower()
        emoji = FINDING_EMOJI.get(status, "❔")
        label = FINDING_ZH.get(status, "未知")
        evidence = str(item.get("evidence", "")).replace("|", "\\|")
        lines.append(f"| {zh} | {emoji} {label} | {evidence} |")
    lines.append("")

    lines.append("## 当前阻塞项")
    lines.append("")
    blockers = result.get("blockers", [])[:5]
    if blockers:
        lines.append("| 优先级 | 缺口 | 影响 |")
        lines.append("| :---: | --- | --- |")
        for b in blockers:
            priority = f"**{b.get('priority')}**" if b.get("priority") == "P1" else b.get("priority")
            gap = str(b.get("gap", "")).replace("|", "\\|")
            impact = str(b.get("impact", "")).replace("|", "\\|")
            lines.append(f"| {priority} | {gap} | {impact} |")
    else:
        lines.append("当前无阻塞项。")
    lines.append("")

    next_steps = result.get("required_changes", [])[:3]
    if next_steps:
        lines.append(f"> **下一步：** {'；'.join(next_steps)}。")
    else:
        lines.append("> **下一步：** 无待办。")
    lines.append("")

    lines.append("## 覆盖情况")
    lines.append("")
    lines.append("| 证据类型 | 覆盖率 |")
    lines.append("| --- | ---: |")
    for zh, key in COVERAGE_ROWS:
        lines.append(f"| {zh} | **{pct(metrics.get(key))}** |")
    lines.append("")

    lines.append("## 生命周期判断")
    lines.append("")
    if decision is None:
        lines.append("**当前状态：⏸ 暂缓裁决**")
        lines.append("")
        lines.append("不是因为 Skill 存在明显质量问题，而是正式生命周期裁决所需证据尚未全部满足。")
        lines.append("")
        provisional = result.get("provisional_direction")
        lines.append(f"当前已知证据更支持：**{PROVISIONAL_ZH.get(provisional, provisional)}**")
        lines.append("")
        lines.append("但在完成认证之前，不将其记录为正式 Lifecycle Decision。")
    else:
        lines.append(f"**当前状态：{decision} · {LIFECYCLE_ZH.get(decision, decision)}（{result.get('lifecycle_status', '')}）**")
        lines.append("")
    why = result.get("why", [])[:5]
    if why:
        lines.append("")
        lines.append("**关键事实：**")
        for item in why:
            lines.append(f"- {item}")
    lines.append("")

    lines.append("## 审计元数据")
    lines.append("")
    lines.append("| 字段 | 值 |")
    lines.append("| --- | --- |")
    lines.append(f"| Protocol | `{result.get('protocol_version', '')}` |")
    lines.append(f"| Protocol Hash | `{result.get('protocol_hash', '')}` |")
    lines.append(f"| Audit Key | `{result.get('audit_key', '')}` |")
    status = result.get("audit_status", "")
    lines.append(f"| Audit Status | `{status}`（{STATUS_ZH.get(status, status)}） |")
    agreement = metrics.get("semantic_agreement")
    lines.append(f"| Semantic Agreement | `{'N/A' if agreement is None else agreement}` |")
    lines.append("")

    lines.append("<details>")
    lines.append("<summary>查看技术说明</summary>")
    lines.append("")
    lines.append(f"- `audit_status = {result.get('audit_status')}`")
    lines.append(f"- `lifecycle_decision = {result.get('lifecycle_decision')}`")
    lines.append(f"- `lifecycle_status = {result.get('lifecycle_status')}`")
    lines.append(f"- `withheld_reason = {result.get('withheld_reason')}`")
    lines.append(f"- `missing_fields = {result.get('missing_fields')}`")
    lines.append(f"- `provisional_direction = {result.get('provisional_direction')}`")
    lines.append(f"- `reproducibility = {result.get('reproducibility')}`")
    lines.append(f"- `semantic_agreement = {agreement}`")
    lines.append(f"- `health_score_status = {health_status}`")
    lines.append(f"- `blocker_count = {result.get('blocker_count')} / p1_blocker_count = {result.get('p1_blocker_count')}`")
    lines.append(f"- `metrics = {metrics}`")
    if result.get("inputs_hash") is not None:
        lines.append(f"- `inputs_hash = {result.get('inputs_hash')}`")
    lines.append("")
    lines.append("正式 Canonical Result 以 `audit-result.json` 为准；本报告为确定性投影，不产生新事实。")
    lines.append("</details>")
    return "\n".join(lines)


def render_en(result: dict) -> str:
    lines = []
    lines.append(f"# 🧩 Skill Audit · `{result.get('target_skill', 'unknown')}`")
    lines.append("")
    lines.append(f"> **Summary:** {build_summary(result)}")
    lines.append("")
    lines.append("## Core Status")
    lines.append("")
    lines.append("| Metric | Status | Note |")
    lines.append("| --- | ---: | --- |")
    lines.append(f"| Health Score | **{result.get('health_score')} / 100** | {result.get('health_score_status', 'PARTIAL')} |")
    metrics = result.get("metrics", {})
    lines.append(f"| Evidence Completeness | **{pct(metrics.get('decision_evidence_coverage'))}** | decision evidence |")
    maturity = result.get("maturity_level") or {}
    cert = result.get("certification_level") or {}
    lines.append(f"| Maturity | **{fmt_level(maturity)}** | |")
    lines.append(f"| Certification | **{fmt_level(cert)}** | |")
    decision = result.get("lifecycle_decision")
    lines.append(f"| Lifecycle | **{'⏸ WITHHELD' if decision is None else decision}** | {result.get('lifecycle_status', '')} |")
    lines.append("")
    lines.append("## Capability Audit")
    lines.append("")
    findings = result.get("findings", {})
    for key, _ in FINDING_KEYS:
        item = findings.get(key, {})
        status = str(item.get("status", "unknown")).lower()
        lines.append(f"- {key}: {FINDING_EMOJI.get(status, '❔')} {item.get('evidence', '')}")
    lines.append("")
    lines.append("## Blockers")
    for b in result.get("blockers", [])[:5]:
        lines.append(f"- [{b.get('priority')}] {b.get('gap')}: {b.get('impact')}")
    if not result.get("blockers"):
        lines.append("- No blockers.")
    lines.append("")
    lines.append(f"> **Next:** {'；'.join(result.get('required_changes', [])[:3])}.")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    for zh, key in COVERAGE_ROWS:
        lines.append(f"- {zh}: {pct(metrics.get(key))}")
    lines.append("")
    lines.append("## Lifecycle")
    if decision is None:
        lines.append(f"**⏸ WITHHELD** — provisional direction: {PROVISIONAL_ZH.get(result.get('provisional_direction'), 'NONE')}")
    else:
        lines.append(f"**{decision}** ({result.get('lifecycle_status', '')})")
    lines.append("")
    lines.append("## Audit Metadata")
    lines.append("")
    lines.append(f"- Protocol: `{result.get('protocol_version', '')}`")
    lines.append(f"- Protocol Hash: `{result.get('protocol_hash', '')}`")
    lines.append(f"- Audit Key: `{result.get('audit_key', '')}`")
    lines.append(f"- Audit Status: `{result.get('audit_status', '')}`")
    lines.append(f"- Semantic Agreement: `{'N/A' if metrics.get('semantic_agreement') is None else metrics.get('semantic_agreement')}`")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>Technical details</summary>")
    lines.append("")
    lines.append(f"- `missing_fields = {result.get('missing_fields')}`")
    lines.append(f"- `withheld_reason = {result.get('withheld_reason')}`")
    lines.append(f"- `metrics = {metrics}`")
    lines.append("")
    lines.append("Canonical result: `audit-result.json`.")
    lines.append("</details>")
    return "\n".join(lines)


def render(result: dict, locale: str) -> str:
    if locale == "en":
        return render_en(result)
    return render_zh(result)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--locale", default="zh-CN")
    args = ap.parse_args()

    result = read_json(args.result)
    md = render(result, args.locale)
    Path(args.out).write_text(md + "\n", encoding="utf-8")
    print(canonical_json({"rendered": True, "locale": args.locale, "out": str(Path(args.out).resolve())}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
