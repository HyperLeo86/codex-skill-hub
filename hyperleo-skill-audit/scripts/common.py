#!/usr/bin/env python3
"""Shared helpers: canonical JSON and content hashing."""
import hashlib
import json
from pathlib import Path


def normalize_bytes(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(normalize_bytes(path.read_bytes())).hexdigest()


def canonical_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def sha256_obj(obj) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def read_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, obj) -> None:
    Path(path).write_text(canonical_json(obj) + "\n", encoding="utf-8")
