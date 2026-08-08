#!/usr/bin/env python3
"""Machine-verify LLM-proposed evidence anchors against the snapshot."""
import argparse
import hashlib
import sys
from pathlib import Path

from common import canonical_json, normalize_bytes, read_json, write_json


def verify_anchor(root: Path, anchor: dict):
    f = anchor.get("file")
    if not f:
        return False, "missing file field"
    p = root / f
    if not p.is_file():
        return False, f"file missing: {f}"
    lines = normalize_bytes(p.read_bytes()).splitlines()
    ls = int(anchor.get("line_start", 1))
    le = int(anchor.get("line_end", ls))
    if ls < 1 or le < ls or le > len(lines):
        return False, f"bad line range {ls}-{le} (file has {len(lines)} lines)"
    joined = b"\n".join(lines[ls - 1:le])
    h = hashlib.sha256(normalize_bytes(joined)).hexdigest()
    qh = anchor.get("quote_hash")
    if qh and qh != h:
        return False, f"quote hash mismatch: {qh} != {h}"
    return True, f"{f}:{ls}-{le} verified"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True)
    ap.add_argument("--semantic", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.target)
    semantic = read_json(args.semantic)
    raw_features = semantic.get("features", semantic)
    verified = {}
    unknown = []
    for key, raw in raw_features.items():
        value = raw.get("value") if isinstance(raw, dict) else raw
        evidence = raw.get("evidence", []) if isinstance(raw, dict) else []
        if not evidence:
            verified[key] = {"value": None, "status": "UNKNOWN", "evidence_verified": False, "evidence": []}
            unknown.append(key)
            continue
        ok_all = True
        detail = []
        for anchor in evidence:
            ok, msg = verify_anchor(root, anchor)
            detail.append({"anchor": anchor, "ok": ok, "detail": msg})
            ok_all = ok_all and ok
        if not ok_all:
            value = None
            unknown.append(key)
        verified[key] = {
            "value": value,
            "status": "KNOWN" if ok_all else "UNKNOWN",
            "evidence_verified": ok_all,
            "evidence": detail,
        }

    out = {
        "verification_version": "1.0.0",
        "features": verified,
        "unknown_fields": sorted(set(unknown)),
    }
    write_json(args.out, out)
    print(
        canonical_json(
            {
                "verified_fields": sum(1 for v in verified.values() if v["status"] == "KNOWN"),
                "unknown_fields": out["unknown_fields"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
