#!/usr/bin/env python3
"""Skill quality checker: structure, token budget, spec, ledger, links.

Usage:
    python3 check_skill.py <skill-dir> [spec.json]

Exit code 1 when any ERROR is found.
"""
import json
import os
import re
import sys
from pathlib import Path

MAX_LINES = 300
MAX_WARN_LINES = 250
MAX_DESC_CHARS = 1024
MIN_TRIGGERS = 6
DISALLOWED = {"README.md", "INSTALLATION_GUIDE.md", "QUICK_REFERENCE.md"}


def rough_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return round((len(text) + cjk * 3) / 4)


def parse_description(front: str) -> str:
    """Parse a folded YAML description scalar (description: >- ...)."""
    m = re.search(r"^description:\s*(?:\>\-?\s*)?\n?((?:\s{2,}.*\n?)+)", front, re.M)
    if m:
        lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
        return " ".join(lines)
    m = re.search(r"^description:\s*(.+)$", front, re.M)
    return m.group(1).strip().strip("'\"") if m else ""


def check_spec(spec_path: str) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    try:
        spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"spec.json 无法解析：{exc}"], []
    if len(spec.get("triggers", [])) < MIN_TRIGGERS:
        errors.append(f"spec triggers 至少 {MIN_TRIGGERS} 条（当前 {len(spec.get('triggers', []))}）")
    if len(spec.get("anti_triggers", [])) < 1:
        errors.append("spec anti_triggers 至少 1 条")
    acceptance = spec.get("input_output", {}).get("acceptance", [])
    if len(acceptance) < 3:
        errors.append(f"spec acceptance 至少 3 条（当前 {len(acceptance)}）")
    if len(spec.get("failure_modes", [])) < 3:
        errors.append(f"spec failure_modes 至少 3 条（当前 {len(spec.get('failure_modes', []))}）")
    budget = spec.get("token_budget", {})
    if not budget.get("skill_md_lines") or not budget.get("skill_md_tokens"):
        errors.append("spec token_budget 必填：skill_md_lines 与 skill_md_tokens")
    return errors, warns


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    spec_path = sys.argv[2] if len(sys.argv) > 2 else None
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
    if not name:
        errors.append("frontmatter 缺少 name")
    else:
        nm = name.group(1).strip()
        if not re.fullmatch(r"[a-z0-9-]{1,64}", nm):
            errors.append(f"name 不合法（仅允许小写字母/数字/连字符，≤64）：{nm}")
        if root.name != nm:
            errors.append(f"name 必须与父目录同名：目录={root.name}，name={nm}")

    desc = parse_description(front)
    if not desc:
        errors.append("frontmatter 缺少 description")
    else:
        if len(desc) > MAX_DESC_CHARS:
            warns.append(f"description 约 {len(desc)} 字符，建议 ≤{MAX_DESC_CHARS}（触发词优先）")
        if not re.search(r"[\u4e00-\u9fffA-Za-z]{2,}", desc):
            errors.append("description 过短，无法触发")

    if "**版本**" not in text and "version" not in front.lower():
        warns.append("SKILL.md 缺少版本行（建议头部一行：**版本**：x.y.z（日期））")

    for bad in DISALLOWED:
        if (root / bad).exists():
            errors.append(f"禁止的人类文档：{bad}")

    refs = root / "references"
    if refs.exists():
        if not (refs / "regressions.md").exists():
            errors.append("references/regressions.md 缺失（回灌断链）；用 build_skill.py 种子化或手动创建")
        for f in sorted(refs.rglob("*")):
            if f.is_file():
                rel = f.relative_to(root)
                if len(rel.parts) > 2:
                    errors.append(f"references 超过一层深：{rel}（保持 references/文件）")
                rtext = f.read_text(encoding="utf-8", errors="ignore")
                rtokens = rough_tokens(rtext)
                if rtokens > 8000:
                    warns.append(f"{rel} 约 {rtokens} token，超预算请加目录/grep 提示")
                if f.stem.lower() not in text.lower() and f.name not in text:
                    warns.append(f"孤儿引用：{rel} 未被 SKILL.md 提及")
    else:
        warns.append("无 references/ 目录：细节建议下沉，账本建议新建")

    scripts = root / "scripts"
    if scripts.exists():
        for f in sorted(scripts.glob("*")):
            if f.is_file():
                if f.suffix == ".py" and not f.read_text(encoding="utf-8", errors="ignore").strip():
                    errors.append(f"空脚本：{f.name}")
                head = f.read_text(encoding="utf-8", errors="ignore")[:64]
                if head.startswith("#!") and not os.access(f, os.X_OK):
                    warns.append(f"脚本未设可执行位：{f.name}（chmod +x）")

    if spec_path:
        spec_errors, _ = check_spec(spec_path)
        errors.extend(spec_errors)

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
