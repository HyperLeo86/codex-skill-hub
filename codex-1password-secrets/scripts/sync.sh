#!/usr/bin/env bash
# codex-1password-secrets sync: pull/push ~/.codex/.env <-> 1Password
#
# 用法:
#   sync.sh pull   # 1Password -> ~/.codex/.env（只写 KEY=VALUE）
#   sync.sh push   # ~/.codex/.env -> 1Password（自动创建/更新字段）
#
# 可配置环境变量:
#   OP_CODEX_VAULT  (默认 Personal)
#   OP_CODEX_ITEM   (默认 "Codex API")
#   CODEX_ENV_FILE  (默认 ~/.codex/.env)
set -euo pipefail

VAULT="${OP_CODEX_VAULT:-Personal}"
ITEM="${OP_CODEX_ITEM:-Codex API}"
ENV_FILE="${CODEX_ENV_FILE:-$HOME/.codex/.env}"
KEYS=(CODEYY_API_KEY OPENAI_CODEX_KEY DEEPSEEK_API_KEY ANTHROPIC_API_KEY ANTHROPIC_BASE_URL EXA_API_KEY)

say() { printf '%s\n' "$*"; }

require_op() {
  command -v op >/dev/null 2>&1 || { say "错误: 找不到 op CLI（brew install 1password-cli）"; exit 1; }
  if ! op whoami >/dev/null 2>&1; then
    say "错误: op 未登录。请先解锁 1Password 桌面端，然后运行:"
    say "  op signin --account my.1password.com"
    exit 1
  fi
  command -v jq >/dev/null 2>&1 || { say "错误: 找不到 jq"; exit 1; }
}

pull() {
  require_op
  local tmp
  tmp="$(mktemp "${TMPDIR:-/tmp}/op-codex-env.XXXXXX")"
  chmod 600 "$tmp"
  for key in "${KEYS[@]}"; do
    if val="$(op read "op://$VAULT/$ITEM/$key" 2>/dev/null)"; then
      printf '%s=%s\n' "$key" "$val" >> "$tmp"
    else
      say "跳过: $key（1Password 中无 op://$VAULT/$ITEM/$key）"
    fi
  done
  mv "$tmp" "$ENV_FILE"
  chmod 600 "$ENV_FILE"
  say "已同步 $ENV_FILE ← 1Password ($VAULT/$ITEM)；文件只含 KEY=VALUE"
}

push() {
  require_op
  [ -f "$ENV_FILE" ] || { say "错误: $ENV_FILE 不存在"; exit 1; }
  local item_ref="op://$VAULT/$ITEM"
  local tmp_dir fields_file item_file edited_file
  tmp_dir="$(mktemp -d "${TMPDIR:-/tmp}/op-codex-sync.XXXXXX")"
  fields_file="$tmp_dir/fields.json"
  item_file="$tmp_dir/item.json"
  edited_file="$tmp_dir/edited.json"
  trap 'rm -rf "$tmp_dir"' EXIT

  # 只读取 KEY=VALUE；注释/空行忽略（契约：.env 不允许注释，这里兜底）
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in ''|'#'*) continue ;; esac
    key="${line%%=*}"
    case "$key" in [A-Za-z_][A-Za-z0-9_]*) ;; *) continue ;; esac
    val="${line#*=}"
    jq -cn --arg k "$key" --arg v "$val" '{id:$k,type:"CONCEALED",label:$k,value:$v}'
  done < "$ENV_FILE" | jq -s -c . > "$fields_file"

  if op item get "$item_ref" --format=json > "$item_file" 2>/dev/null; then
    jq --argjson add "$(cat "$fields_file")" '.fields += $add' "$item_file" > "$edited_file"
    op item edit "$item_ref" --template="$edited_file"
    say "已更新 1Password item: $item_ref"
  else
    op item template get "Secure Note" \
      | jq --arg t "$ITEM" --argjson fields "$(cat "$fields_file")" '.title=$t | .fields=$fields' \
      | op item create --vault "$VAULT" -
    say "已创建 1Password item: $item_ref"
  fi
}

case "${1:-}" in
  pull) pull ;;
  push) push ;;
  *) say "用法: sync.sh {pull|push}"; exit 2 ;;
esac
