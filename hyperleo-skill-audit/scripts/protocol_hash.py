#!/usr/bin/env python3
"""Compute a content-addressed hash over the protocol directory."""
import argparse
import hashlib
import sys
from pathlib import Path

from common import canonical_json, normalize_bytes, write_json


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--protocol-dir", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(args.protocol_dir)
    if not root.is_dir():
        print(canonical_json({"error": f"protocol dir not found: {root}"}))
        return 2

    file_hashes = {}
    digest = hashlib.sha256()
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        h = hashlib.sha256(normalize_bytes(p.read_bytes())).hexdigest()
        file_hashes[rel] = h
        digest.update(rel.encode("utf-8"))
        digest.update(b"\x00")
        digest.update(h.encode("utf-8"))
        digest.update(b"\x00")

    out = {"protocol_hash": digest.hexdigest(), "file_hashes": file_hashes}
    if args.out:
        write_json(args.out, out)
    print(canonical_json(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
