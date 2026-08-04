#!/usr/bin/env python3
"""PRD 机械初检：禁词 / TBD / AC 可测性 / 规则缺例子。

用法：
    python3 validate_prd.py <PRD 路径> [更多 PRD 路径...]

退出码：有错误返回 1，否则 0。
"""
import re
import sys
from pathlib import Path

BANNED = ["尽量", "必要时", "更友好", "体验更好", "合理", "大概", "待定", "TBD", "TODO"]


def check_file(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    for lineno, line in enumerate(lines, 1):
        for word in BANNED:
            if word.lower() in line.lower():
                errors.append(f"{path.name}:{lineno} 禁词「{word}」")

    # 规则必须配例子：规则小节后 20 行内应有「示例」
    for m in re.finditer(r"^#{2,4}\s*(?:规则|Rule)\s+(R\d+)", text, re.M | re.I):
        start = m.end()
        window = text[start : start + 1200]
        if "示例" not in window:
            errors.append(f"{path.name}:{m.start()+1} 规则 {m.group(1)} 缺少示例")

    # AC 可测性：每个 AC- 编号后 8 行内应有 Given/When/Then
    for m in re.finditer(r"AC-\d+(?:\.\d+)?", text):
        start = m.end()
        window = text[start : start + 500]
        if "Given" not in window or "When" not in window or "Then" not in window:
            errors.append(f"{path.name}:{m.start()+1} AC {m.group(0)} 缺少 Given/When/Then")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    all_errors = []
    for arg in sys.argv[1:]:
        all_errors.extend(check_file(Path(arg)))
    if all_errors:
        for e in all_errors:
            print(f"ERROR  {e}")
        return 1
    print("OK：禁词/TBD/AC 可测性/规则示例检查通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
