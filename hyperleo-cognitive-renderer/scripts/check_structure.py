#!/usr/bin/env python3
"""Structural Readability Gate（v0.2）。

只验证结构性可读规范；不声称验证人类理解（Layer B 由 references/readability.md 负责）。

用法：
  python3 check_structure.py <pir.json>

退出码 0 = 通过；1 = 未通过。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = json.loads((ROOT / "protocol" / "pir-schema.json").read_text(encoding="utf-8"))

FALSE_PRECISION = re.compile(r"\b\d+\.\d{3,}\b")


def fail(issues, msg):
    issues.append(f"FAIL  {msg}")


def string_values(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from string_values(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from string_values(v)


def check(ir, issues):
    enums = MANIFEST["enums"]
    limits = MANIFEST["limits"]
    for key in MANIFEST["core_required"]:
        if key not in ir:
            fail(issues, f"缺少 Core PIR 字段：{key}")
            return

    meta = ir["meta"]
    if not meta.get("title"):
        fail(issues, "meta.title 为空")
    if meta.get("task") not in enums["task"]:
        fail(issues, f"meta.task 非法：{meta.get('task')!r}")
    if not meta.get("source"):
        fail(issues, "meta.source 为空（PIR ≠ 事实源，必须声明来源）")

    summary = str(ir.get("summary", ""))
    if not summary.strip():
        fail(issues, "summary 为空")
    elif len(summary) > limits["summary_max_chars"]:
        fail(issues, f"summary 超长（>{limits['summary_max_chars']} 字符）")
    if FALSE_PRECISION.search(summary):
        fail(issues, "summary 数字伪精度（应交给 Compiler 预格式化）")

    claims = ir["claims"]
    if not claims:
        fail(issues, "claims 为空")
    if len(claims) > limits["claims_max"]:
        fail(issues, f"claims 超过 {limits['claims_max']} 条")

    claim_ids = []
    contents = []
    first_screen = 0
    for i, c in enumerate(claims):
        for key in MANIFEST["claim_required"]:
            if key not in c:
                fail(issues, f"claims[{i}] 缺 {key}")
        cid = c.get("claim_id")
        if cid in claim_ids:
            fail(issues, f"claim_id 重复：{cid}")
        claim_ids.append(cid)
        content = str(c.get("content", ""))
        if not content.strip():
            fail(issues, f"claims[{i}] content 为空")
        if content in contents:
            fail(issues, f"claims[{i}] content 重复（重复状态）：{content[:40]}")
        contents.append(content)
        if c.get("derivation_type") not in enums["derivation_type"]:
            fail(issues, f"claims[{i}] derivation_type 非法：{c.get('derivation_type')!r}")
        if c.get("epistemic_state") not in enums["epistemic_state"]:
            fail(issues, f"claims[{i}] epistemic_state 非法：{c.get('epistemic_state')!r}")
        if c.get("priority") not in enums["priority"]:
            fail(issues, f"claims[{i}] priority 非法：{c.get('priority')!r}")
        if c.get("priority") in ("critical", "important"):
            first_screen += 1
        if c.get("derivation_type") != "ASSUMPTION" and not c.get("evidence") and c.get("epistemic_state") != "UNVERIFIED":
            fail(issues, f"claims[{i}] 无 evidence 且非 ASSUMPTION / UNVERIFIED")
        for ref in c.get("evidence", []):
            if not any(e.get("id") == ref for e in ir["evidence"]):
                fail(issues, f"claims[{i}] evidence 引用不存在：{ref}")
        if FALSE_PRECISION.search(content):
            fail(issues, f"claims[{i}] 数字伪精度（应交给 Compiler 预格式化）：{content[:60]}")
    if first_screen > limits["first_screen_critical_important_max"]:
        fail(issues, f"首屏 critical/important 超过 {limits['first_screen_critical_important_max']} 条")

    evidence_ids = []
    for e in ir["evidence"]:
        if not e.get("id") or not e.get("source_id") or not e.get("locator"):
            fail(issues, f"evidence 条目缺 id/source_id/locator：{e!r}")
        eid = e.get("id")
        if eid in evidence_ids:
            fail(issues, f"evidence id 重复：{eid}")
        evidence_ids.append(eid)
        if e.get("verified") not in (True, False):
            fail(issues, f"evidence {eid} 缺 verified 布尔值")

    view = ir["view"]
    vt = view.get("type")
    if vt not in enums["view_type"]:
        fail(issues, f"view.type 非法：{vt!r}")
        return
    for key in MANIFEST["view_required"].get(vt, []):
        if key not in view:
            fail(issues, f"view({vt}) 缺必填字段：{key}")
    if (
        view.get("outcome") is not None
        and view.get("epistemic_state") in ("UNKNOWN", "UNMEASURED")
        and view.get("outcome") in MANIFEST["forbidden_outcome_with_unknown_epistemic"]
    ):
        fail(issues, f"禁止映射：epistemic={view['epistemic_state']} 但 outcome={view['outcome']}")
    for s in string_values(view):
        if FALSE_PRECISION.search(s):
            fail(issues, f"view 数字伪精度（应预格式化）：{s[:60]}")

    technical = ir.get("technical") or {}
    raw_values = [str(v) for v in string_values(technical) if len(str(v)) > 4]
    all_text = summary + " ".join(str(c.get("content", "")) for c in claims)
    for v in raw_values:
        if v in all_text:
            fail(issues, f"技术字段泄漏到首屏/claims：{v[:40]}")


def main():
    if len(sys.argv) < 2:
        print("用法：python3 check_structure.py <pir.json>")
        return 2
    path = Path(sys.argv[1])
    try:
        ir = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL  PIR 无法解析：{exc}")
        return 1
    issues = []
    check(ir, issues)
    if issues:
        print("\n".join(issues))
        print(f"结果：FAIL（{len(issues)} 项）——Structural Gate 未通过")
        return 1
    print(
        f"OK  Structural Gate 通过 · view={ir['view'].get('type')} "
        f"· claims={len(ir['claims'])} · evidence={len(ir['evidence'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
