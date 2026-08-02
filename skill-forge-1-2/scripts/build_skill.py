#!/usr/bin/env python3
"""Spec-driven skill generator for skill-forge-1-2.

Usage:
    python3 build_skill.py <spec.json> --out <output-dir>

The spec follows references/skill-spec.md. Generates a compliant skeleton
(SKILL.md with routing table + agents/openai.yaml); fill in the body after.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_NAME = 64


def build_description(spec: dict) -> str:
    triggers = "；".join(spec.get("triggers", [])[:6]) or "（触发场景待补充）"
    anti = spec.get("anti_triggers") or ["与技能无关的任务"]
    return (
        f"创建或使用「{spec.get('one_liner', spec.get('name', ''))}」技能。"
        f"当用户提出以下说法时触发：{triggers}。"
        f"不用于：{'、'.join(anti)}。"
    )


def write_skill_md(root: Path, spec: dict, description: str) -> None:
    name = spec["name"]
    one_liner = spec.get("one_liner", "")
    io = spec.get("input_output", {})
    freedom = spec.get("freedom", "medium")
    budget = spec.get("token_budget", {})
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "---",
        "",
        f"# {name}",
        "",
        "## 概览",
        "",
        f"{one_liner}",
        "",
        "## 触发与反触发",
        "",
        "- 触发：" + "；".join(spec.get("triggers", [])) or "- 触发：（待补充）",
        "- 反触发：" + "；".join(spec.get("anti_triggers", [])) or "- 反触发：（待补充）",
        "",
        "## 工作流",
        "",
        "1. （由 skill-forge-1-2 根据契约填充：输入处理 → 核心步骤 → 输出）",
        "",
        f"## 验收（来自契约）",
        "",
    ]
    for a in io.get("acceptance", []):
        lines.append(f"- {a}")
    lines += [
        "",
        "## 失败降级",
        "",
    ]
    for fm in spec.get("failure_modes", []):
        lines.append(f"- {fm.get('scenario', '')} → {fm.get('fallback', '')}")
    lines += [
        "",
        "## 资源",
        "",
        "- scripts/：确定性逻辑，直接运行",
        "- references/：按需加载的细节",
        "",
        f"## Token 预算（契约：{budget.get('skill_md_lines', 300)} 行 / {budget.get('skill_md_tokens', 2500)} token，自由度 {freedom}）",
        "",
    ]
    (root / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def write_openai_yaml(root: Path, spec: dict) -> None:
    display = spec.get("display_name", spec["name"])
    short = spec.get("short_description", spec.get("one_liner", ""))[:60]
    default_prompt = spec.get(
        "default_prompt", f"Use ${spec['name']} to {spec.get('one_liner', 'complete the task')}."
    )
    yaml_text = (
        "interface:\n"
        f'  display_name: "{display}"\n'
        f'  short_description: "{short}"\n'
        f'  default_prompt: "{default_prompt}"\n'
    )
    (root / "agents" / "openai.yaml").write_text(yaml_text, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="spec.json 路径")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    name = spec.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        print(f"ERROR：name 必须是小写字母/数字/连字符且 ≤{MAX_NAME}：{name!r}")
        return 1
    if not spec.get("triggers"):
        print("ERROR：契约缺少 triggers（至少 1 条）")
        return 1
    if not spec.get("input_output", {}).get("acceptance"):
        print("ERROR：契约缺少可检查的 acceptance")
        return 1

    root = Path(args.out) / name
    root.mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(exist_ok=True)
    (root / "references").mkdir(exist_ok=True)
    (root / "assets").mkdir(exist_ok=True)
    (root / "agents").mkdir(exist_ok=True)

    description = build_description(spec)
    write_skill_md(root, spec, description)
    write_openai_yaml(root, spec)
    print(f"OK：已生成 {root}")
    print("下一步：由 skill-forge-1-2 填充工作流、失败降级与验收实现，然后运行 check_skill.py。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
