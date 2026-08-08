#!/usr/bin/env python3
"""Deterministic static integrity audit. No LLM judgment."""
import argparse
import json
import re
import sys
from pathlib import Path

from common import canonical_json, read_json, write_json


def run_checks(bundle: dict) -> dict:
    target = bundle["target"]
    root = Path(target["path"])
    files = {f["path"]: f for f in target["files"]}
    entry = bundle.get("entry_file", "SKILL.md")
    results = {}

    def add(name, ok, detail):
        results[name] = {"pass": bool(ok), "detail": detail}

    md_text = ""
    if entry in files:
        md_text = (root / entry).read_text(encoding="utf-8", errors="ignore")
    add("skill_md_exists", entry in files, f"{entry} present" if entry in files else f"missing {entry}")

    spec = {}
    spec_err = ""
    if "spec.json" in files:
        try:
            spec = json.loads((root / "spec.json").read_text(encoding="utf-8"))
        except Exception as exc:
            spec_err = str(exc)
    add("spec_exists", "spec.json" in files, "spec.json present" if "spec.json" in files else "missing spec.json")
    add("spec_parses", "spec.json" in files and not spec_err, spec_err or "spec.json parses")

    contract_ok = bool(
        spec
        and len(spec.get("triggers", [])) >= 6
        and len(spec.get("anti_triggers", [])) >= 1
        and len(spec.get("input_output", {}).get("acceptance", [])) >= 3
        and len(spec.get("failure_modes", [])) >= 3
        and spec.get("token_budget", {}).get("skill_md_lines")
        and spec.get("token_budget", {}).get("skill_md_tokens")
    )
    add("spec_contract_min", contract_ok, "spec contract fields present" if contract_ok else "spec contract incomplete")

    m = re.search(r"^name:\s*(.+)$", md_text, re.M)
    name = m.group(1).strip() if m else ""
    add("name_matches_dir", name == root.name, f"name={name!r} dir={root.name}")
    has_desc = bool(re.search(r"^description:\s*\S", md_text, re.M))
    add("description_present", has_desc, "description present" if has_desc else "missing description")
    add("regressions_ledger_exists", "references/regressions.md" in files, "ledger present" if "references/regressions.md" in files else "missing ledger")

    broken = sorted({ref for ref in re.findall(r"references/([A-Za-z0-9._-]+)", md_text) if f"references/{ref}" not in files})
    add("references_resolve", not broken, f"broken={broken}" if broken else "all references resolve")

    empty_scripts = sorted(
        f
        for f in files
        if f.startswith("scripts/") and f.endswith(".py")
        and not (root / f).read_text(encoding="utf-8", errors="ignore").strip()
    )
    add("scripts_nonempty", not empty_scripts, f"empty={empty_scripts}" if empty_scripts else "all scripts non-empty")

    by_hash = {}
    for f in target["files"]:
        by_hash.setdefault(f["sha256"], []).append(f["path"])
    dups = {h: paths for h, paths in by_hash.items() if len(paths) > 1}
    add("no_duplicate_files", not dups, f"duplicates={dups}" if dups else "no duplicate files")

    vm = re.search(r"\*\*版本\*\*：\s*([0-9]+\.[0-9]+\.[0-9]+)", md_text)
    sv = spec.get("version") if spec else None
    version_ok = vm is None or sv is None or vm.group(1) == str(sv)
    add("version_consistent", version_ok, f"skill={vm.group(1) if vm else 'none'} spec={sv}")

    return results


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--facts-out", required=True)
    args = ap.parse_args()

    bundle = read_json(args.bundle)
    checks = run_checks(bundle)
    total = len(checks)
    passed = sum(1 for c in checks.values() if c["pass"])
    rate = round(passed / total, 4) if total else 0.0

    hard_fail = any(
        checks[k]["pass"] is False
        for k in ("skill_md_exists", "spec_parses", "references_resolve")
    )
    facts = {
        "facts_version": "1.0.0",
        "deterministic_checks": checks,
        "deterministic_check_pass_rate": rate,
        "derived_semantic_inputs": {
            "material_contract_failure": "YES" if hard_fail else "NO",
            "integrity_acceptable": "YES" if rate == 1.0 else "NO",
        },
        "status": "FACTS_OK",
    }
    write_json(args.facts_out, facts)
    print(
        canonical_json(
            {
                "pass": rate == 1.0,
                "pass_rate": rate,
                "failed": [k for k, c in checks.items() if not c["pass"]],
                "derived_semantic_inputs": facts["derived_semantic_inputs"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
