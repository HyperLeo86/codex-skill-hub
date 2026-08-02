#!/usr/bin/env python3
"""Exa 搜索后端：为「检索世界」提供语义检索（可选引擎）。

用法：
  python3 scripts/exa_search.py "查询词" [--num 10] [--type auto|neural|keyword] [--text]

密钥来源（按优先级）：
  1. 环境变量 EXA_API_KEY
  2. ~/.config/jian-suo-shi-jie/exa.env
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

EXA_SEARCH_URL = "https://api.exa.ai/search"


def load_key():
    key = None
    env_file = Path.home() / ".config" / "jian-suo-shi-jie" / "exa.env"
    try:
        import os
        key = os.environ.get("EXA_API_KEY")
    except Exception:
        key = None
    if not key and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("EXA_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("未找到 EXA_API_KEY（环境变量或 ~/.config/jian-suo-shi-jie/exa.env）")
    return key


def search(query, num, stype, with_text):
    payload = {"query": query, "numResults": num, "type": stype}
    if with_text:
        payload["contents"] = {"text": {"maxCharacters": 500}}
    req = urllib.request.Request(
        EXA_SEARCH_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": load_key(),
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description="Exa 搜索（检索世界可选后端）")
    ap.add_argument("query", help="查询词")
    ap.add_argument("--num", type=int, default=10, help="返回条数（默认 10）")
    ap.add_argument("--type", default="auto", choices=["auto", "neural", "keyword"])
    ap.add_argument("--text", action="store_true", help="同时返回正文片段")
    args = ap.parse_args()

    data = search(args.query, args.num, args.type, args.text)
    results = data.get("results", [])
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        date = r.get("publishedDate", "")
        snippet = (r.get("text") or "").replace("\n", " ")[:220]
        print(f"{i}\t{title}\t{url}\t{date}\t{snippet}")


if __name__ == "__main__":
    main()
