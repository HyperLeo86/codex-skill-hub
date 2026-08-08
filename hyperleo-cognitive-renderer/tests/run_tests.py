#!/usr/bin/env python3
"""Golden + boundary + determinism tests（v0.2）。

用法：
  python3 tests/run_tests.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = Path(__file__).resolve().parent
EXAMPLES = ROOT / "assets" / "examples"
GOLDEN = TESTS / "golden"
BOUNDARY = TESTS / "boundary"


def run_script(name, *args):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / name), *map(str, args)],
        capture_output=True,
        text=True,
    )


def main():
    failures = []
    for ex in sorted(EXAMPLES.glob("*.example.json")):
        name = ex.stem.replace(".example", "")
        gate = run_script("check_structure.py", ex)
        if gate.returncode != 0:
            failures.append(f"{name}: Structural Gate FAIL\n{gate.stdout}{gate.stderr}")
            continue
        expected = GOLDEN / f"{name}.expected.md"
        if not expected.exists():
            failures.append(f"{name}: 缺少 golden 期望文件 {expected}")
            continue
        with tempfile.TemporaryDirectory() as tmp:
            out1 = Path(tmp) / "a.md"
            out2 = Path(tmp) / "b.md"
            r1 = run_script("render_md.py", ex, "--out", out1)
            r2 = run_script("render_md.py", ex, "--out", out2)
            if r1.returncode != 0 or r2.returncode != 0:
                failures.append(f"{name}: render 失败\n{r1.stdout}{r1.stderr}{r2.stdout}{r2.stderr}")
                continue
            if out1.read_text(encoding="utf-8") != out2.read_text(encoding="utf-8"):
                failures.append(f"{name}: 确定性失败（两次渲染不一致）")
                continue
            if out1.read_text(encoding="utf-8") != expected.read_text(encoding="utf-8"):
                failures.append(
                    f"{name}: 与 golden 不一致\n--- got ---\n{out1.read_text()}\n--- expected ---\n{expected.read_text()}"
                )
        print(f"PASS  {name}: gate + 确定性 + golden")

    for b in sorted(BOUNDARY.glob("*.json")):
        gate = run_script("check_structure.py", b)
        if gate.returncode == 0:
            failures.append(f"boundary {b.name}: 应 FAIL 但通过")
        else:
            print(f"PASS  boundary {b.name}: 按预期 FAIL")

    if failures:
        print("\n".join(failures))
        print(f"结果：FAIL（{len(failures)} 项）")
        return 1
    print("结果：ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
