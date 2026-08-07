#!/usr/bin/env python3
"""skill-analyst 触发回归检查器（确定性）。

用法：
    python3 check_triggers.py <skill-dir>

检查：
    1. description 包含全部 should-trigger 短语
    2. 反触发段包含全部 should-not 短语
    3. 引号触发句 ≥6，反触发 ≥1

任何一项失败返回 exit 1。修改 SKILL.md / description 后必须重跑。
"""
import argparse
import re
import sys
from pathlib import Path

SHOULD_TRIGGER = [
    "分析一下这个 skill",
    "帮我体检一下这个技能",
    "看看这个 SKILL.md 哪里有问题",
    "这个技能该怎么优化",
    "帮我审查一下技能目录",
    "这个 skill 的逻辑清晰吗",
    "分析一下它的可用性和可维护性",
    "对本地技能库做一次分析",
    "介绍一下这个 skill",
    "给我一张这个技能的身份卡",
]
SHOULD_NOT = [
    "创建/生成一个新技能",
    "把技能发布到 GitHub",
    "帮我检索世界上有没有现成方案",
]
MIN_TRIGGERS = 6


def parse_description(front: str) -> str:
    m = re.search(r"^description:\s*(?:\>\-?\s*)?\n?((?:\s{2,}.*\n?)+)", front, re.M)
    if m:
        return " ".join(ln.strip() for ln in m.group(1).splitlines() if ln.strip())
    m = re.search(r"^description:\s*(.+)$", front, re.M)
    return m.group(1).strip().strip("\"'") if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("skill_dir")
    args = ap.parse_args()
    root = Path(args.skill_dir)
    text = (root / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    front = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    desc = parse_description(front.group(1)) if front else ""
    errors = []
    for phrase in SHOULD_TRIGGER:
        if phrase not in desc:
            errors.append(f"should-trigger 缺失：{phrase}")
    for phrase in SHOULD_NOT:
        if phrase not in desc:
            errors.append(f"should-not 缺失（应出现在反触发）：{phrase}")
    triggers = re.findall(r"「([^」]+)」", desc)
    if len(triggers) < MIN_TRIGGERS:
        errors.append(f"引号触发句 {len(triggers)} 条 < {MIN_TRIGGERS}")
    if "不用于" not in desc:
        errors.append("description 缺少反触发段「不用于」")
    if errors:
        for e in errors:
            print("ERROR", e)
        return 1
    print(f"OK：触发回归通过（触发句 {len(triggers)} 条，反触发 {len(SHOULD_NOT)} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
