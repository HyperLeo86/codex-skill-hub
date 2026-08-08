#!/usr/bin/env python3
"""Deterministic Renderer（v0.2）。

职责：PIR + Presentation Profile + Task View → Markdown。
禁止：判断重要性、改写 summary、猜 risk/action、合并 claim、生成 recommendation。

用法：
  python3 render_md.py <pir.json> [--profile <profile.yaml>] [--out <file.md>]
"""
import argparse
import json
import re
import sys
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROFILE = ROOT / "protocol" / "presentation-profiles" / "hyperleo-default.yaml"
SUPPORTED_VIEWS = {"decision", "diagnosis", "comparison", "monitor"}
UNSUPPORTED_VIEWS = {"browse", "learning"}

EPI_LABEL = {
    "VERIFIED": "已验证", "UNKNOWN": "未知", "UNMEASURED": "未测量",
    "UNSTABLE": "不稳定", "UNVERIFIED": "未验证", "N/A": "不适用",
}
OUTCOME_EMOJI = {
    "POSITIVE": "✅", "NEGATIVE": "❌", "NEUTRAL": "⚪", "HOLD": "🟡",
    "HEALTHY": "✅", "CONCERN": "⚠️", "FAILURE": "❌",
    "KEEP": "✅", "UPGRADE": "🟡", "MERGE": "🟡", "SPLIT": "🟡", "DEPRECATE": "🚫",
}
PRIORITY_ORDER = {"critical": 0, "important": 1, "supporting": 2, "technical": 3}
PRIORITY_LABEL = {"critical": "Critical", "important": "Important", "supporting": "Supporting", "technical": "Technical"}


def load_profile(path):
    """极简 YAML 子集解析（两层缩进 dict + 标量），足够 hyperleo-default。"""
    profile = {}
    stack = [profile]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        key, _, value = raw.strip().partition(":")
        key = key.strip()
        value = value.strip()
        level = 0 if indent == 0 else 1
        while len(stack) > level + 1:
            stack.pop()
        node = stack[-1]
        if value:
            node[key] = value
        else:
            child = {}
            node[key] = child
            stack.append(child)
    return profile


def fmt_number(text, profile):
    numbers = profile.get("numbers", {})
    if not numbers.get("remove_false_precision", True):
        return text
    precision = int(numbers.get("percentage_precision", 0))

    def repl(m):
        x = float(m.group(0))
        if 0 <= x <= 1:
            return f"{round(x * 100, precision):.{precision}f}%"
        return f"{round(x, precision):.{precision}f}" if precision else str(round(x))

    return re.sub(r"\b\d+\.\d{2,}\b", repl, text)


def status_line(view):
    parts = []
    if view.get("outcome") is not None:
        emoji = OUTCOME_EMOJI.get(str(view["outcome"]), "")
        parts.append(f"{emoji} {view['outcome']}".strip())
    elif view.get("state"):
        parts.append(f"🟡 {view['state']}")
    if view.get("epistemic_state"):
        parts.append(f"⬜ {EPI_LABEL.get(view['epistemic_state'], view['epistemic_state'])}")
    return " · ".join(parts) or "概览"


def findings_section(claims):
    if not claims:
        return ""
    lines = ["## 关键发现", ""]
    ordered = sorted(
        claims,
        key=lambda c: (PRIORITY_ORDER.get(c.get("priority"), 9), str(c.get("claim_id", ""))),
    )
    for c in ordered:
        tag = PRIORITY_LABEL.get(c.get("priority"), str(c.get("priority", "")))
        line = f"- **[{tag}]** {c['content']} `{c.get('epistemic_state', '')}`"
        if c.get("derivation_type") == "ASSUMPTION":
            line += " `ASSUMPTION`"
        refs = ", ".join(f"[{r}](#证据)" for r in c.get("evidence", []))
        if refs:
            line += f" {refs}"
        lines.append(line.rstrip())
    return "\n".join(lines)


def evidence_section(evidence):
    lines = ["## 证据", "", "| id | source_id | locator | detail | 状态 |", "| --- | --- | --- | --- | --- |"]
    for e in evidence:
        lines.append(
            f"| {e['id']} | {e.get('source_id', '')} | {e.get('locator', '')} "
            f"| {e.get('detail', '')} | {'✅' if e.get('verified') else '❔ 未核验'} |"
        )
    return "\n".join(lines)


def technical_section(technical):
    if not technical:
        return ""
    lines = ["<details>", "<summary>原始字段与技术元数据（L4）</summary>", ""]
    for k, v in (technical.get("fields") or {}).items():
        lines.append(f"- `{k}`: `{v}`")
    if technical.get("raw"):
        lines += ["", "```", str(technical["raw"]), "```"]
    lines += ["", "</details>"]
    return "\n".join(lines)


def list_section(title, items):
    if not items:
        return ""
    lines = [f"## {title}", ""]
    lines += [f"- {item}" for item in items]
    return "\n".join(lines)


def render_decision(pir, profile):
    view = pir["view"]
    lines = []
    for key, label in (("state", "状态"), ("reason", "原因"), ("risk", "风险"), ("action", "行动")):
        if view.get(key):
            lines.append(f"**{label}**：{fmt_number(str(view[key]), profile)}")
    blockers = view.get("blockers") or []
    if blockers:
        lines.append("**阻断项**：" + "；".join(str(b) for b in blockers))
    return {
        "title": pir["meta"]["title"],
        "status_line": status_line(view),
        "summary": fmt_number(pir["summary"], profile),
        "decision_block": "\n".join(lines),
        "findings_section": findings_section(pir["claims"]),
        "evidence_section": evidence_section(pir["evidence"]),
        "technical_section": technical_section(pir.get("technical")),
    }


def render_comparison(pir, profile):
    view = pir["view"]
    dims = view["dimensions"]
    items = view["items"]
    values = view.get("values") or {}
    table = ["| 项目 | " + " | ".join(dims) + " |", "| --- | " + " | ".join(["---"] * len(dims)) + " |"]
    for item in items:
        iid = item.get("id", "")
        label = item.get("label", iid)
        row = [fmt_number(str(values.get(iid, {}).get(d, "")), profile) for d in dims]
        table.append(f"| {label} | " + " | ".join(row) + " |")
    return {
        "title": pir["meta"]["title"],
        "status_line": status_line(view),
        "summary": fmt_number(pir["summary"], profile),
        "comparison_table": "\n".join(table),
        "differences_section": list_section("关键差异", view.get("key_differences") or []),
        "tradeoffs_section": list_section("权衡", view.get("tradeoffs") or []),
        "recommendation_section": f"## 推荐\n\n{view['recommendation']}" if view.get("recommendation") else "",
        "evidence_section": evidence_section(pir["evidence"]),
        "technical_section": technical_section(pir.get("technical")),
    }


def render_monitor(pir, profile):
    view = pir["view"]
    state = view.get("current_state") or {}
    table = ["| 组件/指标 | 状态 |", "| --- | --- |"]
    for k, v in state.items():
        table.append(f"| {k} | {fmt_number(str(v), profile)} |")
    return {
        "title": pir["meta"]["title"],
        "status_line": "监控概览",
        "summary": fmt_number(pir["summary"], profile),
        "status_table": "\n".join(table),
        "changes_section": list_section("变化", view.get("changes") or []),
        "exceptions_section": list_section("异常", view.get("exceptions") or []),
        "actions_section": list_section("需要处理", view.get("action_required") or []),
        "evidence_section": evidence_section(pir["evidence"]),
        "technical_section": technical_section(pir.get("technical")),
    }


def template_name(view_type):
    return "decision" if view_type in ("decision", "diagnosis") else view_type


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pir", type=Path)
    ap.add_argument("--profile", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    pir = json.loads(args.pir.read_text(encoding="utf-8"))
    vt = pir.get("view", {}).get("type")
    if vt in UNSUPPORTED_VIEWS:
        print(f"ERROR  v0.2 未实现视图：{vt}（支持：{sorted(SUPPORTED_VIEWS)}）")
        return 2
    if vt not in SUPPORTED_VIEWS:
        print(f"ERROR  未知 view.type：{vt!r}")
        return 2

    profile = load_profile(args.profile or DEFAULT_PROFILE)
    tpl = Template((ROOT / "templates" / f"{template_name(vt)}.md").read_text(encoding="utf-8"))
    if vt in ("decision", "diagnosis"):
        variables = render_decision(pir, profile)
    elif vt == "comparison":
        variables = render_comparison(pir, profile)
    else:
        variables = render_monitor(pir, profile)
    md = tpl.safe_substitute(variables).strip() + "\n"

    if args.out:
        args.out.write_text(md, encoding="utf-8")
        print(f"已渲染（{vt}）：{args.out}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
