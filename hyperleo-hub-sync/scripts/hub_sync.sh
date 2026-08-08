#!/usr/bin/env bash
# hyperleo-hub-sync: pull latest codex-skill-hub and refresh ~/.codex/skills
# Env overrides: HUB_REPO, HUB_BRANCH, HUB_MIRROR_DIR, CODEX_SKILLS_DIR,
#                HUB_BACKUP_DIR, DRY_RUN
set -euo pipefail

HUB_REPO="${HUB_REPO:-https://github.com/HyperLeo86/codex-skill-hub.git}"
HUB_BRANCH="${HUB_BRANCH:-main}"
MIRROR_DIR="${HUB_MIRROR_DIR:-$HOME/.codex/skill-hub}"
TARGET_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
BACKUP_DIR="${HUB_BACKUP_DIR:-$HOME/.codex/skill-hub-backups}"
DRY_RUN="${DRY_RUN:-0}"

repo_name() { basename "${1%/}" .git; }

install_skill_dir() {
  local src="$1" dst="$2" tmp
  tmp="${dst}.tmp.$$"
  rm -rf "$tmp"
  cp -R "$src" "$tmp"
  mv "$tmp" "$dst"
}

echo "==> 1/3 拉取仓库: $HUB_REPO ($HUB_BRANCH)"
if [[ "$DRY_RUN" == "1" ]]; then
  echo "DRY_RUN：跳过 clone/pull"
  [[ -d "$MIRROR_DIR" ]] || { echo "错误：mirror 不存在: $MIRROR_DIR（先用真实模式同步一次）"; exit 1; }
else
  if [[ -d "$MIRROR_DIR/.git" ]]; then
    origin_url=$(git -C "$MIRROR_DIR" remote get-url origin 2>/dev/null || true)
    if [[ -z "$origin_url" || "$(repo_name "$origin_url")" != "$(repo_name "$HUB_REPO")" ]]; then
      echo "错误：mirror origin（$origin_url）与目标仓库（$HUB_REPO）不一致，拒绝 fetch/reset"
      exit 1
    fi
    git -C "$MIRROR_DIR" fetch --depth 1 origin "$HUB_BRANCH"
    git -C "$MIRROR_DIR" reset --hard "origin/$HUB_BRANCH"
  else
    git clone --depth 1 --branch "$HUB_BRANCH" "$HUB_REPO" "$MIRROR_DIR"
  fi
fi

echo "==> 2/3 比对并同步技能"
if [[ "$DRY_RUN" != "1" ]]; then
  mkdir -p "$TARGET_DIR" "$BACKUP_DIR"
fi

added=()
updated=()
unchanged=()
skipped=()

while IFS= read -r skill_dir; do
  name=$(basename "$skill_dir")
  if [[ ! -f "$skill_dir/SKILL.md" ]]; then
    skipped+=("$name")
    continue
  fi
  dest="$TARGET_DIR/$name"
  if [[ ! -d "$dest" ]]; then
    added+=("$name")
    [[ "$DRY_RUN" == "1" ]] || install_skill_dir "$skill_dir" "$dest"
  elif diff -qr "$skill_dir" "$dest" >/dev/null 2>&1; then
    unchanged+=("$name")
  else
    ts=$(date +%Y%m%d-%H%M%S)
    backup="$BACKUP_DIR/$name-$ts"
    updated+=("$name -> $backup")
    if [[ "$DRY_RUN" != "1" ]]; then
      mv "$dest" "$backup"
      install_skill_dir "$skill_dir" "$dest"
    fi
  fi
done < <(find "$MIRROR_DIR" -mindepth 1 -maxdepth 1 -type d -not -name '.*' -print | sort)

echo "==> 3/3 结果"
printf '新增 (%d)：%s\n' "${#added[@]}" "${added[*]:-无}"
printf '更新 (%d)：%s\n' "${#updated[@]}" "${updated[*]:-无}"
printf '未变 (%d)：%s\n' "${#unchanged[@]}" "${unchanged[*]:-无}"
[[ ${#skipped[@]} -gt 0 ]] && printf '跳过（无 SKILL.md）(%d)：%s\n' "${#skipped[@]}" "${skipped[*]}"

if [[ -d "$TARGET_DIR" ]]; then
  local_only=()
  while IFS= read -r d; do
    name=$(basename "$d")
    [[ -d "$MIRROR_DIR/$name" ]] || local_only+=("$name")
  done < <(find "$TARGET_DIR" -mindepth 1 -maxdepth 1 -type d -not -name '.*' -print | sort)
  [[ ${#local_only[@]} -gt 0 ]] && printf '本地独有（未在仓库中，需人工决定）(%d)：%s\n' "${#local_only[@]}" "${local_only[*]}"
fi

[[ "$DRY_RUN" == "1" ]] && echo "DRY_RUN：未写入任何目标文件"
echo "完成。新技能/更新在下一次对话生效。"
