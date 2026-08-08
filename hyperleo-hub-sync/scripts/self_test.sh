#!/usr/bin/env bash
# self-test for hyperleo-hub-sync: local fixture regression, no network needed
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$HERE/hub_sync.sh"

TEST_ROOT="$(mktemp -d)"
trap 'rm -rf "$TEST_ROOT"' EXIT

FIXTURE="$TEST_ROOT/fixture"
MIRROR="$TEST_ROOT/mirror"
TARGET="$TEST_ROOT/skills"
BACKUP="$TEST_ROOT/backup"

fail() { echo "FAIL: $1"; exit 1; }

# 1) fixture repo with two skills
mkdir -p "$FIXTURE/skill-a" "$FIXTURE/skill-b"
printf -- '---\nname: skill-a\ndescription: 测试技能 A\n---\n# A\n' > "$FIXTURE/skill-a/SKILL.md"
printf -- '---\nname: skill-b\ndescription: 测试技能 B\n---\n# B\n' > "$FIXTURE/skill-b/SKILL.md"
git -C "$FIXTURE" init -q
git -C "$FIXTURE" checkout -q -b main
git -C "$FIXTURE" config user.email test@example.com
git -C "$FIXTURE" config user.name test
git -C "$FIXTURE" add -A
git -C "$FIXTURE" commit -q -m init

# 2) first sync installs all
HUB_REPO="$FIXTURE" HUB_MIRROR_DIR="$MIRROR" CODEX_SKILLS_DIR="$TARGET" HUB_BACKUP_DIR="$BACKUP" \
  bash "$SYNC_SCRIPT" >/dev/null
[[ -f "$TARGET/skill-a/SKILL.md" && -f "$TARGET/skill-b/SKILL.md" ]] || fail "首次同步未安装全部技能"

# 3) local edit + local-only dir -> update backs up and restores, local-only kept
echo "# local edit" >> "$TARGET/skill-a/SKILL.md"
mkdir -p "$TARGET/legacy-skill"
printf -- '---\nname: legacy-skill\ndescription: 本地独有\n---\n' > "$TARGET/legacy-skill/SKILL.md"
HUB_REPO="$FIXTURE" HUB_MIRROR_DIR="$MIRROR" CODEX_SKILLS_DIR="$TARGET" HUB_BACKUP_DIR="$BACKUP" \
  bash "$SYNC_SCRIPT" >/dev/null
grep -q "local edit" "$TARGET/skill-a/SKILL.md" && fail "本地改动未被还原"
[[ -d "$TARGET/legacy-skill" ]] || fail "本地独有技能被删除"
[[ -d "$BACKUP" && "$(find "$BACKUP" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')" -ge 1 ]] || fail "更新未生成备份"

# 4) remote update -> next sync applies
echo "# remote v2" >> "$FIXTURE/skill-b/SKILL.md"
git -C "$FIXTURE" add -A
git -C "$FIXTURE" commit -q -m v2
HUB_REPO="$FIXTURE" HUB_MIRROR_DIR="$MIRROR" CODEX_SKILLS_DIR="$TARGET" HUB_BACKUP_DIR="$BACKUP" \
  bash "$SYNC_SCRIPT" >/dev/null
grep -q "remote v2" "$TARGET/skill-b/SKILL.md" || fail "远端更新未同步"

# 5) wrong mirror origin must be rejected before fetch/reset
WRONG="$TEST_ROOT/wrong"
git init -q "$WRONG"
git -C "$WRONG" checkout -q -b main
git -C "$WRONG" config user.email test@example.com
git -C "$WRONG" config user.name test
git -C "$WRONG" commit -q --allow-empty -m wrong
if HUB_REPO="$FIXTURE" HUB_MIRROR_DIR="$WRONG" CODEX_SKILLS_DIR="$TARGET" HUB_BACKUP_DIR="$BACKUP" \
  bash "$SYNC_SCRIPT" >/dev/null 2>&1; then
  fail "origin 校验未拦截错误 mirror"
fi

# 6) dry-run must not write target files
BEFORE=$(find "$TARGET" -type f -print0 | sort -z | xargs -0 shasum 2>/dev/null || true)
HUB_REPO="$FIXTURE" HUB_MIRROR_DIR="$MIRROR" CODEX_SKILLS_DIR="$TARGET" HUB_BACKUP_DIR="$BACKUP" DRY_RUN=1 \
  bash "$SYNC_SCRIPT" >/dev/null
AFTER=$(find "$TARGET" -type f -print0 | sort -z | xargs -0 shasum 2>/dev/null || true)
[[ "$BEFORE" == "$AFTER" ]] || fail "DRY_RUN 写入了目标文件"

echo "PASS: self-test 全部通过（新增/更新/备份/本地独有/远端更新/origin 校验/dry-run）"
