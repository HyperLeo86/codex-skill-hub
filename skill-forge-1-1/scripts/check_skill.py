#!/usr/bin/env python3
"""Skill quality checker: structure, token budget, links, orphan files.

Usage:
    python3 check_skill.py <skill-dir>

Exit code 1 when any ERROR is found.
"""
import re
import sys
from pathlib import Path

MAX_LINES = 300
MAX_WARN_LINES = 250
MAX_DESC_CHARS = 400
DISALLOWED = {"README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}


def rough_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return round((len(text) + cjk * 3) / 4)


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    errors, warns = [], []

    skill_md = root / "SKILL.md"
    if not skill_md.exists():
        errors.append("SKILL.md 不存在")
        print_issues(errors, warns)
        return 1

    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > MAX_LINES:
        errors.append(f"SKILL.md {len(lines)} 行，超过 {MAX_LINES} 行硬预算")
    elif len(lines) > MAX_WARN_LINES:
        warns.append(f"SKILL.md {len(lines)} 行，接近预算，建议拆分")

    tokens = rough_tokens(text)
    if tokens > 2500:
        errors.append(f"SKILL.md 约 {tokens} token，超过 2500 预算")
    else:
        warns.append(f"SKILL.md 约 {tokens} token")

    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    front = m.group(1) if m else ""
    name = re.search(r"^name:\s*(.+)$", front, re.M)
    desc = re.search(r"^description:\s*(.+)$", front, re.M | re.S)
    if not name:
        errors.append("frontmatter 缺少 name")
    elif not re.fullmatch(r"[a-z0-9-]{1,64}", name.group(1).strip()):
        errors.append(f"name 不合法（仅允许小写字母/数字/连字符，≤64）：{name.group(1).strip()}")
    if not desc:
        errors.append("frontmatter 缺少 description")
    else:
        d = desc.group(1).strip().strip("'\"")
        if len(d) > MAX_DESC_CHARS:
            warns.append(f"description 约 {len(d)} 字符，建议 ≤{MAX_DESC_CHARS}（触发词优先）")
        if not re.search(r"[\u4e00-\u9fffA-Za-z]{2,}", d):
            errors.append("description 过短，无法触发")

    for bad in DISALLOWED:
        if (root / bad).exists():
            errors.append(f"禁止的人类文档：{bad}")

    refs = root / "references"
    if refs.exists():
        for f in sorted(refs.rglob("*")):
            if f.is_file():
                rtext = f.read_text(encoding="utf-8", errors="ignore")
                rtokens = rough_tokens(rtext)
                if rtokens > 8000:
                    warns.append(f"{f.name} 约 {rtokens} token，超 10k 词预算请加目录/grep 提示")
                if f.stem.lower() not in text.lower() and f.name not in text:
                    warns.append(f"孤儿引用：{f.name} 未被 SKILL.md 提及")

    scripts = root / "scripts"
    if scripts.exists():
        for f in sorted(scripts.glob("*")):
            if f.suffix == ".py" and not f.read_text(encoding="utf-8", errors="ignore").strip():
                errors.append(f"空脚本：{f.name}")

    print_issues(errors, warns)
    return 1 if errors else 0


def print_issues(errors, warns):
    for e in errors:
        print(f"ERROR  {e}")
    for w in warns:
        print(f"WARN   {w}")
    if not errors and not warns:
        print("OK：结构、预算、引用检查全部通过")
    elif not errors:
        print("PASS（有 WARN，建议处理）")


if __name__ == "__main__":
    sys.exit(main())
