#!/usr/bin/env python3
"""Compare two semantic extraction runs on decision-critical fields only.

semantic_agreement must be null unless an independent semantic reproduction
was actually performed (--independent). Otherwise the status is UNVERIFIED.
"""
import argparse
import json
import sys
from pathlib import Path

from common import canonical_json, read_json, write_json


def flatten(run: dict) -> dict:
    raw = run.get("features", run)
    out = {}
    for k, v in raw.items():
        out[k] = v.get("value") if isinstance(v, dict) else v
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-a", required=True)
    ap.add_argument("--run-b", required=True)
    ap.add_argument("--critical-fields", required=True)
    ap.add_argument("--independent", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    fields_path = Path(args.critical_fields)
    if fields_path.is_file():
        critical = json.loads(fields_path.read_text(encoding="utf-8"))
        critical = critical.get("decision_critical_fields", critical) if isinstance(critical, dict) else critical
    else:
        critical = [c.strip() for c in args.critical_fields.split(",") if c.strip()]

    a, b = flatten(read_json(args.run_a)), flatten(read_json(args.run_b))
    disagreements = []
    for field in critical:
        va, vb = a.get(field), b.get(field)
        if va != vb:
            disagreements.append({"field": field, "run_a": va, "run_b": vb})
    total = len(critical)

    if not args.independent:
        out = {
            "semantic_agreement": None,
            "semantic_status": "UNVERIFIED",
            "compared_fields": total,
            "disagreements": [],
            "note": "independent semantic reproduction not performed; agreement is not claimed",
        }
    else:
        agreement = round((total - len(disagreements)) / total, 4) if total else 1.0
        out = {
            "semantic_agreement": agreement,
            "semantic_status": "STABLE" if agreement == 1.0 else "UNSTABLE",
            "compared_fields": total,
            "disagreements": disagreements,
        }
    write_json(args.out, out)
    print(canonical_json(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
