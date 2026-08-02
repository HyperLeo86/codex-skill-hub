#!/usr/bin/env python3
"""Tavily 搜索后端：为「检索世界」提供结构化交叉验证（第二引擎）。

用法：
  python3 scripts/tavily_search.py "查询词" [--num 5] [--text]

密钥来源（按优先级）：
  1. 环境变量 TAVILY_API_KEY
  2. ~/.config/jian-suo-shi-jie/tavily.env
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

TAVILY_URL = "https://api.tavily.com/search"


def load_key():
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        env_file = Path.home() / ".config" / "jian-suo-shi-jie" / "tavily.env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("TAVILY_API_KEY="):
                    key = line.split("=", 1)[1].strip()
    if not key:
        sys.exit("未找到 TAVILY_API_KEY（环境变量或 ~/.config/jian-suo-shi-jie/tavily.env）")
    return key


def search(query, num, with_text):
    payload = {
        "api_key": load_key(),
        "query": query,
        "max_results": num,
        "include_raw_content": with_text,
    }
    req = urllib.request.Request(
        TAVILY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description="Tavily 搜索（检索世界第二引擎）")
    ap.add_argument("query", help="查询词")
    ap.add_argument("--num", type=int, default=5, help="返回条数（默认 5）")
    ap.add_argument("--text", action="store_true", help="同时输出正文片段")
    args = ap.parse_args()

    data = search(args.query, args.num, args.text)
    for i, r in enumerate(data.get("results", []), 1):
        title = r.get("title", "")
        url = r.get("url", "")
        date = r.get("published_date", "")
        snippet = (r.get("content") or "").replace("\n", " ")[:220]
        print(f"{i}\t{title}\t{url}\t{date}\t{snippet}")


if __name__ == "__main__":
    main()
