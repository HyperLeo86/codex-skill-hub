#!/usr/bin/env python3
"""Deterministic Health Score / Maturity / Certification / coverage metrics.

Health Score is computed from structured check results only and never
participates in the Lifecycle Decision.
"""
import argparse
import json
import sys
from pathlib import Path

from common import canonical_json, read_json, write_json

ROOT = Path(__file__).resolve().parent.parent
EXPECTED_TYPES = ["SKILL.md", "spec.json", "references", "scripts", "tests", "protocol"]


def _present(target_files, prefix):
    return any(p == prefix or p.startswith(prefix + "/") for p in target_files)


def compute(
    bundle: dict,
    facts: dict,
    features: dict,
    repro: dict,
    behavior: dict,
    independent_repro: bool,
    certified: bool,
    scoring: dict,
    target_root: Path,
) -> dict:
    checks = facts.get("deterministic_checks", {})
    target_files = {f["path"] for f in bundle.get("target", {}).get("files", [])}

    weights = scoring["health_score"]["weights"]
    health_score = round(sum(w for name, w in weights.items() if checks.get(name, {}).get("pass")))
    health_score = max(0, min(100, health_score))

    snapshot_coverage = round(
        sum(1 for t in EXPECTED_TYPES if _present(target_files, t)) / len(EXPECTED_TYPES),
        4,
    )

    critical = []
    schema_path = ROOT / "protocol" / "semantic-schema.json"
    if schema_path.is_file():
        critical = json.loads(schema_path.read_text(encoding="utf-8")).get("decision_critical_fields", [])
    feature_status = {}
    if features:
        for k, v in features.get("features", {}).items():
            feature_status[k] = v.get("status") if isinstance(v, dict) else ("KNOWN" if v is not None else "UNKNOWN")
    facts_known = set(facts.get("derived_semantic_inputs", {}).keys())
    decision_known = sum(1 for f in critical if feature_status.get(f) == "KNOWN" or f in facts_known)
    decision_evidence_coverage = round(decision_known / len(critical), 4) if critical else 0.0

    usage_coverage = 1.0 if bundle.get("usage_evidence") else 0.0

    behavior_present = bool(behavior)
    behavior_test_pass = bool(behavior and behavior.get("test_suite_pass"))
    behavior_coverage = 1.0 if behavior_test_pass else (0.5 if behavior_present else 0.0)

    repro_done = bool(independent_repro and repro and repro.get("semantic_status") in ("STABLE", "UNSTABLE"))
    reproducibility_coverage = 1.0 if repro_done else 0.0
    semantic_agreement = repro.get("semantic_agreement") if independent_repro and repro else None

    if health_score == 100 and decision_evidence_coverage == 1.0:
        health_score_status = "VERIFIED"
    elif health_score == 100:
        health_score_status = "PARTIAL"
    else:
        health_score_status = "PROVISIONAL"

    ledger_path = target_root / "references" / "regressions.md"
    regressions_all_fixed = False
    if ledger_path.is_file():
        regressions_all_fixed = not any("未修复" in line for line in ledger_path.read_text(encoding="utf-8").splitlines())

    cond = {
        "skill_md_exists": bool(checks.get("skill_md_exists", {}).get("pass")),
        "spec_parses": bool(checks.get("spec_parses", {}).get("pass")),
        "references_resolve": bool(checks.get("references_resolve", {}).get("pass")),
        "tests_exist": _present(target_files, "tests"),
        "behavior_test_suite_pass": behavior_test_pass,
        "calibration_exists": _present(target_files, "tests/calibration"),
        "regressions_all_fixed": regressions_all_fixed,
        "changelog_exists": "CHANGELOG.md" in target_files,
        "protocol_lock_exists": "protocol/protocol.lock.json" in target_files,
        "independent_repro_stable": bool(independent_repro and repro and repro.get("semantic_status") == "STABLE"),
        "certified_artifact_exists": bool(certified),
        "snapshot_complete": bool(bundle.get("target") and bundle.get("evidence_bundle_hash")),
        "facts_present": facts.get("status") == "FACTS_OK",
        "calibration_pass": bool(behavior and behavior.get("calibration_pass")),
        "migration_pass": bool(behavior and behavior.get("migration_pass")),
    }

    maturity_key = "L1_Prototype"
    for key in ("L5_Certified", "L4_Governed", "L3_Tested", "L2_Structured", "L1_Prototype"):
        requires = scoring["maturity_levels"][key]["requires"]
        if all(cond[r] for r in requires):
            maturity_key = key
            break

    if cond["certified_artifact_exists"]:
        certification_key = "C4_Certified"
    elif cond["calibration_pass"] and cond["migration_pass"]:
        certification_key = "C3_GovernedCalibrated"
    elif cond["independent_repro_stable"]:
        certification_key = "C2_SemanticVerified"
    elif cond["snapshot_complete"] and cond["facts_present"]:
        certification_key = "C1_EvidenceCollected"
    else:
        certification_key = "C0_NotCertified"

    blockers = []
    self_audit = str(target_root.resolve()) == str(ROOT.resolve())
    if self_audit:
        blockers.append(scoring["blockers"]["self_audit_bias"])
    if usage_coverage == 0:
        blockers.append(scoring["blockers"]["usage_missing"])
    if not repro_done:
        blockers.append(scoring["blockers"]["repro_missing"])
    if repro and repro.get("semantic_status") == "UNSTABLE":
        blockers.append(scoring["blockers"]["semantic_unstable"])
    if facts.get("status") != "FACTS_OK":
        blockers.append(scoring["blockers"]["facts_incomplete"])
    if behavior_coverage < 1.0:
        blockers.append(scoring["blockers"]["behavior_incomplete"])
    priority_order = {"P1": 0, "P2": 1}
    blockers.sort(key=lambda b: priority_order.get(b["priority"], 9))

    def level(key):
        code = key.split("_", 1)[0]
        name = key.split("_", 1)[1]
        return {"level": code, "name": name}

    return {
        "scoring_version": scoring.get("scoring_version"),
        "skill_name": Path(bundle["target"]["path"]).name,
        "health_score": health_score,
        "health_score_status": health_score_status,
        "health_score_rule": "deterministic weights from protocol/scoring.json; not used in Lifecycle Decision",
        "maturity_level": level(maturity_key),
        "certification_level": level(certification_key),
        "semantic_agreement": semantic_agreement,
        "reproducibility_status": repro.get("semantic_status") if repro else None,
        "self_audit": self_audit,
        "blockers": blockers,
        "blocker_count": len(blockers),
        "p1_blocker_count": sum(1 for b in blockers if b["priority"] == "P1"),
        "metrics": {
            "snapshot_coverage": snapshot_coverage,
            "decision_evidence_coverage": decision_evidence_coverage,
            "usage_coverage": usage_coverage,
            "behavior_coverage": behavior_coverage,
            "reproducibility_coverage": reproducibility_coverage,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--facts", required=True)
    ap.add_argument("--features", default=None)
    ap.add_argument("--repro", default=None)
    ap.add_argument("--behavior", default=None)
    ap.add_argument("--independent-repro", action="store_true")
    ap.add_argument("--certified", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    scoring = json.loads((ROOT / "protocol" / "scoring.json").read_text(encoding="utf-8"))
    bundle = read_json(args.bundle)
    facts = read_json(args.facts)
    features = read_json(args.features) if args.features and Path(args.features).is_file() else None
    repro = read_json(args.repro) if args.repro and Path(args.repro).is_file() else None
    behavior = read_json(args.behavior) if args.behavior and Path(args.behavior).is_file() else None
    target_root = Path(bundle["target"]["path"])

    result = compute(
        bundle=bundle,
        facts=facts,
        features=features,
        repro=repro,
        behavior=behavior,
        independent_repro=args.independent_repro,
        certified=args.certified,
        scoring=scoring,
        target_root=target_root,
    )
    write_json(args.out, result)
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
