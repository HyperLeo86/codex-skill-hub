#!/usr/bin/env python3
"""Spec-driven skill generator for skill-forge.

Usage:
    python3 build_skill.py <spec.json> --out <output-dir>

The spec follows references/skill-spec.md. Generates a compliant skeleton:
SKILL.md (routing + decision-rights clause + acceptance), references/
regressions.md ledger seed, and agents/openai.yaml. Fill in the body after.
"""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_NAME = 64
MAX_DESC_TRIGGERS = 8
MIN_TRIGGERS = 6


def build_description(spec: dict) -> str:
    one_liner = spec.get("one_liner") or spec.get("name", "")
    triggers = spec.get("triggers", [])[:MAX_DESC_TRIGGERS]
    trigger_txt = "；".join(f"「{t}」" for t in triggers) or "（触发场景待补充）"
    anti = spec.get("anti_triggers") or ["与技能无关的任务"]
    return (
        f"{one_liner}。当用户说 {trigger_txt} 时使用；"
        f"不用于：{'、'.join(anti)}。"
    )


def decision_rights(freedom: str) -> list[str]:
    table = {
        "low": [
            "以脚本/步骤为准，顺序、参数、输出格式禁止即兴偏离",
            "脚本输出是唯一事实源，禁止覆盖或重算",
        ],
        "medium": [
            "按伪代码/模板执行，参数可依上下文调整",
            "输出格式遵循模板，内容允许合理变化",
        ],
        "high": [
            "只遵守原则与验收标准，具体路径由 agent 自行判断",
            "自由度内允许探索，但验收不合格必须降级或停止",
        ],
    }
    return table.get(freedom, table["medium"])


def write_skill_md(root: Path, spec: dict, description: str) -> None:
    name = spec["name"]
    one_liner = spec.get("one_liner", "")
    io = spec.get("input_output", {})
    freedom = spec.get("freedom", "medium")
    budget = spec.get("token_budget", {})
    rights = decision_rights(freedom)
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        "---",
        "",
        f"# {name}",
        "",
        f"**版本**：0.1.0（{spec.get('date', '待填')}）",
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
        f"## 决定权（自由度 {freedom}）",
        "",
    ]
    for r in rights:
        lines.append(f"- {r}")
    lines += [
        "",
        "## 工作流",
        "",
        "1. （由 skill-forge 根据契约填充：输入处理 → 核心步骤 → 输出）",
        "",
        "## 验收（来自契约）",
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
        "- references/：按需加载的细节（含回归账本 regressions.md）",
        "",
        f"## Token 预算（契约：{budget.get('skill_md_lines', 300)} 行 / {budget.get('skill_md_tokens', 2500)} token）",
        "",
    ]
    (root / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")


def write_regressions_seed(root: Path) -> None:
    seed = (
        "# 回归账本（保留最近 10 条）\n"
        "\n"
        "| 日期 | 场景 | 失败 | 修复 | 状态 |\n"
        "| --- | --- | --- | --- | --- |\n"
        "|（首次使用后按 validation.md 格式追加，升级前全量回归）| | | | |\n"
    )
    (root / "references" / "regressions.md").write_text(seed, encoding="utf-8")


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


def validate_spec(spec: dict) -> list[str]:
    errors = []
    name = spec.get("name", "")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        errors.append(f"name 必须是小写字母/数字/连字符且 ≤{MAX_NAME}：{name!r}")
    if len(spec.get("triggers", [])) < MIN_TRIGGERS:
        errors.append(f"triggers 至少 {MIN_TRIGGERS} 条（当前 {len(spec.get('triggers', []))}）")
    if len(spec.get("anti_triggers", [])) < 1:
        errors.append("anti_triggers 至少 1 条")
    acceptance = spec.get("input_output", {}).get("acceptance", [])
    if len(acceptance) < 3:
        errors.append(f"acceptance 至少 3 条（当前 {len(acceptance)}）")
    if len(spec.get("failure_modes", [])) < 3:
        errors.append(f"failure_modes 至少 3 条（当前 {len(spec.get('failure_modes', []))}）")
    budget = spec.get("token_budget", {})
    if not budget.get("skill_md_lines") or not budget.get("skill_md_tokens"):
        errors.append("token_budget 必填：skill_md_lines 与 skill_md_tokens")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", help="spec.json 路径")
    ap.add_argument("--out", required=True, help="输出目录")
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    errors = validate_spec(spec)
    if errors:
        for e in errors:
            print(f"ERROR {e}")
        return 1

    root = Path(args.out) / spec["name"]
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "references").mkdir(exist_ok=True)
    (root / "assets").mkdir(exist_ok=True)
    (root / "agents").mkdir(exist_ok=True)

    description = build_description(spec)
    write_skill_md(root, spec, description)
    write_regressions_seed(root)
    write_openai_yaml(root, spec)
    print(f"OK：已生成 {root}")
    print("下一步：由 skill-forge 填充工作流与失败降级实现，然后运行 check_skill.py <skill-dir> <spec.json>。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
