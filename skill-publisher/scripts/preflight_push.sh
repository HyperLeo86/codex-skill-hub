#!/usr/bin/env bash
# skill-publisher 发布前置检查（commit/tag/push 前必跑）
#
# 用法：bash scripts/preflight_push.sh [仓库目录]
# 检查：remote 协议 → SSH agent / 回退钥匙 → HTTPS 写权限（git push --dry-run）
# 任一项失败返回 exit 1，并输出可执行的修复指引。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="${1:-}"
if [ -z "$REPO_DIR" ]; then
  REPO_DIR="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
fi
if [ -z "$REPO_DIR" ] || [ ! -d "$REPO_DIR/.git" ]; then
  echo "❌ 未找到仓库根：请从 codex-skill-hub 仓库内运行，或显式传入仓库目录参数"
  exit 1
fi
cd "$REPO_DIR"

fail() { echo "❌ $*"; exit 1; }
pass() { echo "✅ $*"; }

REMOTE="$(git config --get remote.origin.url || true)"
[ -n "$REMOTE" ] || fail "未配置 remote.origin.url"
echo "remote: $REMOTE"

if [[ "$REMOTE" == git@* ]]; then
  echo "--- SSH 协议：检测 ssh-agent 身份 ---"
  AGENT_OUT="$(ssh -o BatchMode=yes -o ConnectTimeout=10 -T git@github.com 2>&1 || true)"
  if echo "$AGENT_OUT" | grep -q "successfully authenticated"; then
    pass "SSH agent 认证可用"
  else
    FALLBACK="$HOME/.ssh/neo/neo_git_ed25519"
    FALLBACK_OUT=""
    if [ -f "$FALLBACK" ]; then
      FALLBACK_OUT="$(ssh -i "$FALLBACK" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10 -T git@github.com 2>&1 || true)"
    fi
    if echo "$FALLBACK_OUT" | grep -q "successfully authenticated"; then
      pass "SSH agent 不可用，但回退钥匙可用：推送时加 GIT_SSH_COMMAND=\"ssh -i $FALLBACK -o IdentitiesOnly=yes\""
    else
      fail "SSH 认证失败：请 ssh-add 或解锁 1Password SSH agent；或确认回退钥匙 $FALLBACK 可用"
    fi
  fi
else
  echo "--- HTTPS 协议：git push --dry-run 验证写权限（无副作用）---"
  if git push --dry-run origin main >/dev/null 2>&1; then
    pass "HTTPS 写权限可用"
  else
    fail "HTTPS 写权限被拒：请给 PAT 加 Contents: Read and write，或运行 gh auth login 换 OAuth token"
  fi
fi

echo "✅ Preflight 通过：可以进入 commit → tag → push"
