#!/usr/bin/env python3
"""同步仓库 README 技能清单（发布前必跑，幂等）。

用法：
    python3 update_readme.py [仓库目录]   # 默认当前目录

行为：
    - 扫描含 SKILL.md 的一层技能目录
    - 从 SKILL.md 读取 name / **版本** / description 首句
    - 替换 README 中「| 技能 | 版本 | 说明 |」表格行（按目录名排序）
    - 无变化时不写文件（幂等）
"""
import re
import sys
from pathlib import Path


def parse_skill(root: Path):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    front = m.group(1) if m else ""
    nm = re.search(r"^name:\s*(.+)$", front, re.M)
    name = nm.group(1).strip() if nm else root.name
    dm = re.search(r"^description:\s*(?:\>\-?\s*)?\n?((?:\s{2,}.*\n?)+)", front, re.M)
    if dm:
        desc = " ".join(ln.strip() for ln in dm.group(1).splitlines() if ln.strip())
    else:
        d2 = re.search(r"^description:\s*(.+)$", front, re.M)
        desc = d2.group(1).strip().strip("\"'") if d2 else ""
    ver = re.search(r"\*\*版本\*\*：([0-9.]+)", text)
    version = ver.group(1) if ver else "?"
    one = desc.split("。")[0].strip() if desc else name
    if len(one) > 90:
        one = one[:90] + "…"
    return name, version, one


def main():
    repo = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    readme = repo / "README.md"
    if not readme.exists():
        sys.exit(f"ERROR: {readme} 不存在")
    skills = []
    for d in sorted(repo.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists():
            skills.append(parse_skill(d))
    if not skills:
        sys.exit("ERROR: 未找到任何含 SKILL.md 的技能目录")
    lines = readme.read_text(encoding="utf-8").splitlines()
    try:
        idx = next(i for i, l in enumerate(lines) if l.strip().startswith("| 技能") and "版本" in l)
    except StopIteration:
        sys.exit("ERROR: README 缺少「| 技能 | 版本 | 说明 |」表头")
    sep = idx + 1
    if not (sep < len(lines) and re.fullmatch(r"\|\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|", lines[sep].strip())):
        sys.exit("ERROR: README 技能清单缺少分隔行（|---|）")
    start = sep + 1
    end = start
    while end < len(lines) and lines[end].strip().startswith("|"):
        end += 1
    rows = [f"| {n} | {v} | {o} |" for n, v, o in skills]
    out = "\n".join(lines[:start] + rows + lines[end:]) + "\n"
    if out == readme.read_text(encoding="utf-8"):
        print("OK: README 已同步（无变化）")
        return 0
    readme.write_text(out, encoding="utf-8")
    print(f"OK: README 已更新（{len(skills)} 个技能）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
