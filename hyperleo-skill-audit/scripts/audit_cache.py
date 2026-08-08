#!/usr/bin/env python3
"""Content-addressed audit cache: derive AuditKey, store/get certified results."""
import argparse
import hashlib
import sys
from pathlib import Path

from common import canonical_json, read_json, write_json


def derive_key(evidence_hash: str, protocol_hash: str) -> str:
    return hashlib.sha256(f"{evidence_hash}{protocol_hash}".encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence-hash", required=True)
    ap.add_argument("--protocol-hash", required=True)
    ap.add_argument("--cache-dir", required=True)
    ap.add_argument("--get", action="store_true")
    ap.add_argument("--store", default=None)
    args = ap.parse_args()

    key = derive_key(args.evidence_hash, args.protocol_hash)
    entry = Path(args.cache_dir) / key
    certificate = entry / "certificate.json"

    if args.store:
        result = read_json(args.store)
        if "audit_key" not in result:
            print(canonical_json({"error": "audit_key missing in result", "derived": key}))
            return 2
        if result["audit_key"] != key:
            print(
                canonical_json(
                    {
                        "error": "audit_key mismatch",
                        "derived": key,
                        "in_result": result["audit_key"],
                    }
                )
            )
            return 2
        entry.mkdir(parents=True, exist_ok=True)
        write_json(certificate, result)
        write_json(entry / "audit-result.json", result)
        print(canonical_json({"stored": True, "audit_key": key, "path": str(certificate)}))
        return 0

    if args.get:
        if certificate.is_file():
            result = read_json(certificate)
            print(canonical_json({"cache": "HIT", "audit_key": key, "result": result}))
            return 0
        print(canonical_json({"cache": "MISS", "audit_key": key}))
        return 1

    print(canonical_json({"audit_key": key}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
