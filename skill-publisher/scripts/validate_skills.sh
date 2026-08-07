#!/usr/bin/env bash
# skill-publisher 自动校验门（发布前必跑）
#
# 校验内容：
#   1) gh skill publish --fix —— GitHub 官方 agentskills 规范校验 + 仓库安全检查
#   2) skills-ref validate    —— agentskills 参考库逐技能校验（全库扫描）
#
# 用法：bash scripts/validate_skills.sh [仓库目录，默认自动探测 git root]
# 说明：--fix 可能修改元数据，若输出显示有改动，请先 review 再提交。
set -euo pipefail

fail() { echo "❌ $*" >&2; exit 1; }
pass() { echo "✅ $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${1:-}"
if [ -z "$REPO_DIR" ]; then
  REPO_DIR="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [ -z "$REPO_DIR" ] || [ ! -d "$REPO_DIR/.git" ]; then
  fail "未找到仓库根：请从 codex-skill-hub 仓库内运行（bash skill-publisher/scripts/validate_skills.sh），或显式传入仓库目录参数"
fi
cd "$REPO_DIR"

# --- 1. gh skill（GitHub 官方校验） ---
if ! gh skill --help >/dev/null 2>&1; then
  fail "未检测到 gh skill（需要 GitHub CLI ≥ 2.90，可 brew upgrade gh）"
fi
pass "gh skill 可用"
echo "--- gh skill publish --fix（若修改文件，请先 review 再提交） ---"
gh skill publish --fix || fail "gh skill 校验未通过"
pass "gh skill publish 校验通过"

# --- 2. skills-ref（agentskills 参考库） ---
find_skills_ref() {
  if command -v skills-ref >/dev/null 2>&1; then command -v skills-ref; return 0; fi
  local cand="$HOME/.local/skills-ref-venv/bin/skills-ref"
  if [ -x "$cand" ]; then echo "$cand"; return 0; fi
  return 1
}

SKILLS_REF="$(find_skills_ref || true)"
if [ -z "$SKILLS_REF" ]; then
  echo "--- 首次运行：安装 skills-ref 到 ~/.local/skills-ref-venv ---"
  PY_BIN=""
  for cand in "${SKILLS_REF_PYTHON:-}" python3.12 python3.11 python3; do
    [ -n "$cand" ] || continue
    if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
      PY_BIN="$(command -v "$cand")"
      break
    fi
  done
  [ -n "$PY_BIN" ] || fail "需要 Python ≥3.11 来安装 skills-ref（可设置 SKILLS_REF_PYTHON 指定解释器）"

  SRC_DIR="${SKILLS_REF_SRC:-$HOME/.cache/skills-ref-src}"
  if [ ! -d "$SRC_DIR/.git" ]; then
    mkdir -p "$SRC_DIR"
    git clone -q --depth 1 https://github.com/agentskills/agentskills.git "$SRC_DIR"
  fi
  if [ ! -x "$HOME/.local/skills-ref-venv/bin/skills-ref" ]; then
    "$PY_BIN" -m venv "$HOME/.local/skills-ref-venv"
    "$HOME/.local/skills-ref-venv/bin/pip" install -q -e "$SRC_DIR/skills-ref"
  fi
  SKILLS_REF="$HOME/.local/skills-ref-venv/bin/skills-ref"
fi
pass "skills-ref 可用：$SKILLS_REF"

echo "--- skills-ref validate（逐技能） ---"
count=0
for d in */; do
  [ -f "${d}SKILL.md" ] || continue
  "$SKILLS_REF" validate "$d" || fail "skills-ref 校验失败：$d"
  pass "skills-ref validate ${d%/}"
  count=$((count + 1))
done
[ "$count" -gt 0 ] || fail "没有找到任何技能目录（含 SKILL.md）"

echo ""
pass "校验门全绿：gh skill + skills-ref 均通过（共 $count 个技能）"
