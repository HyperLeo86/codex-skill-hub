#!/usr/bin/env python3
"""skill-analyst 静态事实收集器（确定性）。

用法：
    python3 analyze_skill.py <skill-dir> [--json]

输出：SKILL.md 行数/token、description 长度、引用文件存在性、
脚本可执行位、版本行、章节列表、账本存在性。
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path


def rough_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return round((len(text) + cjk * 3) / 4)


def parse_description(front: str) -> str:
    """支持单行与折叠（>-）两种 YAML description。"""
    m = re.search(r"^description:\s*(?:\>\-?\s*)?\n?((?:\s{2,}.*\n?)+)", front, re.M)
    if m:
        return " ".join(ln.strip() for ln in m.group(1).splitlines() if ln.strip())
    m = re.search(r"^description:\s*(.+)$", front, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("skill_dir", help="目标 skill 目录")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()
    root = Path(args.skill_dir)
    facts = {"dir": str(root.resolve()), "errors": []}
    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        facts["errors"].append("SKILL.md 不存在")
        print(json.dumps(facts, ensure_ascii=False, indent=2) if args.json else "ERROR SKILL.md 不存在")
        return 1

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    facts["lines"] = len(lines)
    facts["tokens"] = rough_tokens(text)
    front = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    front_text = front.group(1) if front else ""
    name = re.search(r"^name:\s*(.+)$", front_text, re.M)
    facts["name"] = name.group(1).strip() if name else None
    desc = parse_description(front_text)
    facts["desc_chars"] = len(desc)
    facts["desc"] = (desc[:160] + "…") if len(desc) > 160 else desc
    ver = re.search(r"\*\*版本\*\*[：:]\s*([0-9.]+)\s*[（(]([^）)]+)[）)]", text)
    facts["version"] = {"version": ver.group(1), "date": ver.group(2)} if ver else None
    facts["sections"] = re.findall(r"^##\s+(.+)$", text, re.M)

    facts["references"] = []
    refs_dir = root / "references"
    if refs_dir.exists():
        for f in sorted(refs_dir.glob("*.md")):
            facts["references"].append({"name": f.name, "exists": True, "tokens": rough_tokens(f.read_text(encoding="utf-8", errors="ignore"))})
    facts["scripts"] = []
    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        for f in sorted(scripts_dir.iterdir()):
            if f.is_file():
                head = f.read_text(encoding="utf-8", errors="ignore")[:2]
                facts["scripts"].append({"name": f.name, "executable": os.access(f, os.X_OK), "shebang": head == "#!"})
    facts["ledger_exists"] = (refs_dir / "regressions.md").exists() if refs_dir else False

    # 资源章节引用核验
    resource_refs = re.findall(r"(?:references|scripts|assets)/[A-Za-z0-9_./-]+\.(?:md|py|sh|json|yaml|yml|txt)", text)
    missing = []
    for ref in sorted(set(resource_refs)):
        if not (root / ref).exists():
            missing.append(ref)
    facts["missing_references"] = missing

    if args.json:
        print(json.dumps(facts, ensure_ascii=False, indent=2))
    else:
        print(f"name={facts['name']} lines={facts['lines']} tokens={facts['tokens']} desc_chars={facts['desc_chars']} version={facts['version']}")
        print(f"references={[r['name'] for r in facts['references']]}")
        print(f"scripts={[s['name'] for s in facts['scripts']]}")
        print(f"ledger={facts['ledger_exists']} missing={facts['missing_references']}")
        for e in facts["errors"]:
            print("ERROR", e)
    return 0 if not facts["errors"] and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
