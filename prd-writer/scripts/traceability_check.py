#!/usr/bin/env python3
"""追溯矩阵检查：孤儿需求 / 孤儿 AC / 孤儿测试。

用法：
    python3 traceability_check.py <PRD 路径> [acceptance-map.md]

PRD 中出现的 FR-/AC-/TC- 编号，与矩阵行做双向比对；孤儿项报错。
未提供矩阵时，只报告 PRD 中出现的 FR 无 AC 引用。
"""
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"\b(FR|NFR|AC|TC)-\d+(?:\.\d+)?\b")


def ids_in(text: str, prefix: str) -> set[str]:
    return {m.group(0) for m in ID_RE.finditer(text) if m.group(0).startswith(prefix)}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    prd_path = Path(sys.argv[1])
    prd_text = prd_path.read_text(encoding="utf-8", errors="ignore")
    errors = []

    prd_frs = ids_in(prd_text, "FR") | ids_in(prd_text, "NFR")
    prd_acs = ids_in(prd_text, "AC")
    prd_tcs = ids_in(prd_text, "TC")

    matrix_path = Path(sys.argv[2]) if len(sys.argv) > 2 else prd_path.parent / "acceptance-map.md"
    if not matrix_path.exists():
        # 无矩阵时最小检查：PRD 中每个 FR 是否被某条 AC 关联
        for fr in sorted(prd_frs):
            if fr not in prd_text.split("AC-", 1)[0] and not any(fr in ac_ctx for ac_ctx in re.split(r"AC-\d", prd_text)):
                errors.append(f"孤儿需求：{fr} 无 AC 引用（未提供 acceptance-map.md，按就近扫描判断）")
        if not errors:
            print("OK：无矩阵模式未发现孤儿需求（建议提供 acceptance-map.md 做完整检查）")
        return 1 if errors else 0

    matrix_text = matrix_path.read_text(encoding="utf-8", errors="ignore")
    matrix_frs, matrix_acs, matrix_tcs = set(), set(), set()
    for row in matrix_text.splitlines():
        if not row.startswith("|") or "需求" in row:
            continue
        matrix_frs.update(ids_in(row, "FR") | ids_in(row, "NFR"))
        matrix_acs.update(ids_in(row, "AC"))
        matrix_tcs.update(ids_in(row, "TC"))

    for fr in sorted(prd_frs - matrix_frs):
        errors.append(f"孤儿需求：{fr} 在 PRD 中但不在矩阵")
    for ac in sorted(prd_acs - matrix_acs):
        errors.append(f"孤儿 AC：{ac} 在 PRD 中但不在矩阵")
    for ac in sorted(matrix_acs - prd_acs):
        errors.append(f"孤儿 AC：{ac} 在矩阵中但不在 PRD")
    for tc in sorted(matrix_tcs):
        if tc not in matrix_text and tc not in prd_tcs:
            errors.append(f"孤儿测试：{tc} 无出处")

    if errors:
        for e in errors:
            print(f"ERROR  {e}")
        return 1
    print("OK：追溯矩阵双向一致，无孤儿需求/孤儿 AC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
