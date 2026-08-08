#!/usr/bin/env python3
"""Build an immutable evidence snapshot of a target skill and neighbors."""
import argparse
import sys
from pathlib import Path

from common import canonical_json, file_sha256, sha256_obj, write_json

SKIP_DIRS = {".audit", "__pycache__", ".git"}


def snapshot_dir(path: Path) -> dict:
    files = []
    for p in sorted(path.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(path)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files.append(
            {
                "path": rel.as_posix(),
                "sha256": file_sha256(p),
                "size": p.stat().st_size,
            }
        )
    return {"path": str(path.resolve()), "files": files, "hash": sha256_obj(files)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--target", required=True)
    ap.add_argument("--skill-file", default="SKILL.md")
    ap.add_argument("--neighbors", nargs="*", default=[])
    ap.add_argument("--usage", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    target_path = Path(args.target)
    if not target_path.is_dir() or not (target_path / args.skill_file).is_file():
        print(
            canonical_json(
                {
                    "error": "INVALID_INPUT",
                    "detail": f"target missing or has no {args.skill_file}: {target_path}",
                }
            )
        )
        return 2

    target = snapshot_dir(target_path)
    neighbors = [snapshot_dir(Path(n)) for n in args.neighbors if Path(n).is_dir()]
    usage = [snapshot_dir(Path(u)) for u in args.usage if Path(u).is_dir()]

    bundle = {
        "target": target,
        "neighbors": neighbors,
        "usage_evidence": usage,
        "entry_file": args.skill_file,
        "volatile_metadata_removed": True,
    }
    bundle["evidence_bundle_hash"] = sha256_obj(
        {
            "target": target["hash"],
            "neighbors": [n["hash"] for n in neighbors],
            "usage_evidence": [u["hash"] for u in usage],
        }
    )
    write_json(args.out, bundle)
    print(
        canonical_json(
            {
                "evidence_bundle_hash": bundle["evidence_bundle_hash"],
                "target_hash": target["hash"],
                "out": str(Path(args.out).resolve()),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
