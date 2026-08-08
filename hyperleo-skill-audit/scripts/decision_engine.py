#!/usr/bin/env python3
"""Deterministic lifecycle decision engine. No LLM.

audit_status and lifecycle_decision are strictly orthogonal:
- audit_status describes whether this audit itself is reliable.
- lifecycle_decision is null (WITHHELD) when the evidence required by the
  specific decision rule is missing; INSUFFICIENT_EVIDENCE is never a
  lifecycle decision.
"""
import argparse
import sys
from pathlib import Path

from common import canonical_json, read_json, sha256_obj, write_json

ALLOWED_STATUS = {"CERTIFIED", "HUMAN_ADJUDICATED"}

RULES = [
    {
        "id": "split",
        "required": ["multiple_independent_jobs", "each_job_independent"],
        "test": lambda f: f.get("multiple_independent_jobs") == "YES" and f.get("each_job_independent") == "YES",
    },
    {
        "id": "merge",
        "required": ["duplicate_relationship", "unique_value"],
        "test": lambda f: f.get("duplicate_relationship") in ("DUPLICATE", "SUBSET") and f.get("unique_value") == "NO",
    },
    {
        "id": "deprecate",
        "required": ["unique_value", "replaceability", "unique_assets", "usage_frequency"],
        "test": lambda f: f.get("unique_value") == "NO"
        and f.get("replaceability") == "HIGH"
        and f.get("unique_assets") == "NO"
        and f.get("usage_frequency") != "HIGH",
    },
    {
        "id": "upgrade",
        "required": [
            "identity_clear",
            "value_established",
            "material_contract_failure",
            "behavior_failure",
            "integrity_acceptable",
            "dependency_healthy",
        ],
        "test": lambda f: f.get("identity_clear") == "YES"
        and f.get("value_established") == "YES"
        and (
            f.get("material_contract_failure") == "YES"
            or f.get("behavior_failure") == "YES"
            or f.get("integrity_acceptable") == "NO"
            or f.get("dependency_healthy") == "NO"
        ),
    },
    {
        "id": "keep",
        "required": [
            "identity_clear",
            "value_established",
            "integrity_acceptable",
            "dependency_healthy",
            "unique_position",
            "deletion_loss_described",
            "duplicate_relationship",
            "behavior_failure",
            "material_contract_failure",
            "usage_frequency",
        ],
        "test": lambda f: f.get("identity_clear") == "YES"
        and f.get("value_established") == "YES"
        and f.get("integrity_acceptable") == "YES"
        and f.get("dependency_healthy") == "YES"
        and f.get("unique_position") == "YES"
        and f.get("deletion_loss_described") == "YES"
        and f.get("duplicate_relationship") in ("NONE", "INDEPENDENT", "COMPLEMENTARY")
        and f.get("behavior_failure") == "NO"
        and f.get("material_contract_failure") == "NO"
        and f.get("usage_frequency") not in (None, "UNKNOWN"),
    },
]

KEEP_EXPECTED = {
    "identity_clear": "YES",
    "value_established": "YES",
    "integrity_acceptable": "YES",
    "dependency_healthy": "YES",
    "unique_position": "YES",
    "deletion_loss_described": "YES",
    "duplicate_relationship": ("NONE", "INDEPENDENT", "COMPLEMENTARY"),
    "behavior_failure": "NO",
    "material_contract_failure": "NO",
}


def provisional_direction(features: dict) -> str:
    """Candidate direction for human reference only; never a formal decision."""
    for rule in RULES:
        if all(features.get(f) not in (None, "UNKNOWN") for f in rule["required"]) and rule["test"](features):
            return f"{rule['id'].upper()}_CANDIDATE"
    missing = [f for f in RULES[-1]["required"] if features.get(f) in (None, "UNKNOWN")]
    if missing == ["usage_frequency"]:
        keep_ok = True
        for field, expected in KEEP_EXPECTED.items():
            val = features.get(field)
            if (val not in expected) if isinstance(expected, tuple) else (val != expected):
                keep_ok = False
                break
        if keep_ok:
            return "KEEP_CANDIDATE"
    return "NONE"


def normalize(raw: dict) -> dict:
    out = {}
    for k, v in raw.items():
        if isinstance(v, dict) and "value" in v:
            val = v.get("value")
        elif isinstance(v, str) or v is None:
            val = v
        else:
            val = None
        out[k] = None if val in (None, "UNKNOWN", "unknown", "") else str(val).upper()
    return out


def decide(features: dict) -> dict:
    missing = set()
    for rule in RULES:
        unknowns = [f for f in rule["required"] if features.get(f) in (None, "UNKNOWN")]
        if unknowns:
            missing.update(unknowns)
            continue
        if rule["test"](features):
            return {
                "lifecycle_decision": rule["id"].upper(),
                "lifecycle_status": "ISSUED",
                "rule_applied": rule["id"],
                "missing_fields": [],
                "provisional_direction": None,
            }
    if missing:
        return {
            "lifecycle_decision": None,
            "lifecycle_status": "WITHHELD",
            "rule_applied": None,
            "missing_fields": sorted(missing),
            "withheld_reason": "missing_required_evidence",
            "provisional_direction": provisional_direction(features),
        }
    return {
        "lifecycle_decision": None,
        "lifecycle_status": "WITHHELD",
        "rule_applied": None,
        "missing_fields": [],
        "withheld_reason": "no_rule_matched",
        "provisional_direction": provisional_direction(features),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--features", required=True)
    ap.add_argument("--facts", default=None)
    ap.add_argument("--behavior", default=None)
    ap.add_argument("--audit-status", default="CERTIFIED")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    raw = read_json(args.features)
    features = normalize(raw.get("features", raw))
    if args.facts and Path(args.facts).is_file():
        derived = read_json(args.facts).get("derived_semantic_inputs", {})
        for k, v in derived.items():
            features.setdefault(k, None if v in (None, "UNKNOWN") else str(v).upper())
    if args.behavior and Path(args.behavior).is_file():
        for k, v in read_json(args.behavior).items():
            features.setdefault(k, None if v in (None, "UNKNOWN") else str(v).upper())

    status = str(args.audit_status).upper()
    if status not in ALLOWED_STATUS:
        result = {
            "lifecycle_decision": None,
            "lifecycle_status": "WITHHELD",
            "rule_applied": None,
            "missing_fields": [],
            "withheld_reason": f"audit_status={status} not certifiable",
            "provisional_direction": provisional_direction(features),
        }
    else:
        result = decide(features)
    result["audit_status"] = status
    result["inputs_hash"] = sha256_obj({"features": features, "status": status})
    write_json(args.out, result)
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
