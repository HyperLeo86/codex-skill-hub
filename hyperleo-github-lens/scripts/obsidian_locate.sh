#!/usr/bin/env bash
# Locate the Obsidian vault for hyperleo-github-lens.
# Priority: $OBSIDIAN_VAULT -> open vault in obsidian.json -> first vault.
set -uo pipefail

if [ -n "${OBSIDIAN_VAULT:-}" ] && [ -d "$OBSIDIAN_VAULT" ]; then
  echo "$OBSIDIAN_VAULT"
  exit 0
fi

REGISTRY="$HOME/Library/Application Support/obsidian/obsidian.json"
if [ ! -f "$REGISTRY" ]; then
  echo "OBSIDIAN_VAULT_NOT_FOUND" >&2
  exit 1
fi

OPEN_PATH=$(jq -r '.vaults | to_entries[] | select(.value.open == true) | .value.path' "$REGISTRY" 2>/dev/null | head -1)
if [ -n "$OPEN_PATH" ] && [ -d "$OPEN_PATH" ]; then
  echo "$OPEN_PATH"
  exit 0
fi

FIRST_PATH=$(jq -r '.vaults | to_entries[0].value.path' "$REGISTRY" 2>/dev/null)
if [ -n "$FIRST_PATH" ] && [ -d "$FIRST_PATH" ]; then
  echo "$FIRST_PATH"
  exit 0
fi

echo "OBSIDIAN_VAULT_NOT_FOUND" >&2
exit 1
