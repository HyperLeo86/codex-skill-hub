#!/usr/bin/env bash
# L1 deterministic metadata fetcher for hyperleo-github-lens.
# Usage: repo_meta.sh owner/repo [output.json]
set -uo pipefail

REPO="${1:-}"
OUT="${2:-}"
if [ -z "$REPO" ]; then
  echo '{"error":"usage: repo_meta.sh owner/repo"}' >&2
  exit 2
fi

meta=$(curl -s --max-time 30 "https://api.github.com/repos/${REPO}" || true)
score=$(curl -s --max-time 30 "https://api.securityscorecards.dev/projects/github.com/${REPO}" || true)
deps=$(curl -s --max-time 30 "https://api.deps.dev/v3alpha/systems/GitHub/repositories/${REPO}" || true)

stars=$(printf '%s' "$meta" | jq -r 'if has("stargazers_count") then (.stargazers_count|tostring) else "unavailable" end' 2>/dev/null)
stars="${stars:-unavailable}"
forks=$(printf '%s' "$meta" | jq -r 'if has("forks_count") then (.forks_count|tostring) else "unavailable" end' 2>/dev/null)
forks="${forks:-unavailable}"
open_issues=$(printf '%s' "$meta" | jq -r 'if has("open_issues_count") then (.open_issues_count|tostring) else "unavailable" end' 2>/dev/null)
open_issues="${open_issues:-unavailable}"
archived=$(printf '%s' "$meta" | jq -r 'if has("archived") then (.archived|tostring) else "unavailable" end' 2>/dev/null)
archived="${archived:-unavailable}"
license=$(printf '%s' "$meta" | jq -r 'if .license != null then (.license.spdx_id // "unavailable") else "unavailable" end' 2>/dev/null)
license="${license:-unavailable}"
pushed_at=$(printf '%s' "$meta" | jq -r '.pushed_at // "unavailable"' 2>/dev/null)
pushed_at="${pushed_at:-unavailable}"
created_at=$(printf '%s' "$meta" | jq -r '.created_at // "unavailable"' 2>/dev/null)
created_at="${created_at:-unavailable}"
language=$(printf '%s' "$meta" | jq -r '.language // "unavailable"' 2>/dev/null)
language="${language:-unavailable}"
description=$(printf '%s' "$meta" | jq -r '.description // "unavailable"' 2>/dev/null)
description="${description:-unavailable}"
topics=$(printf '%s' "$meta" | jq -c '.topics // []' 2>/dev/null)
topics="${topics:-[]}"

ratio_sf="unavailable"; ratio_si="unavailable"; fork_rate="unavailable"
if [ "$stars" != "unavailable" ] && [ "$forks" != "unavailable" ] && [ "${forks:-0}" != "0" ]; then
  ratio_sf=$(awk -v s="$stars" -v f="$forks" 'BEGIN { printf "%.2f", s/f }')
  fork_rate=$(awk -v s="$stars" -v f="$forks" 'BEGIN { printf "%.2f", f*100/s }')
fi
if [ "$stars" != "unavailable" ] && [ "$open_issues" != "unavailable" ] && [ "${open_issues:-0}" != "0" ]; then
  ratio_si=$(awk -v s="$stars" -v i="$open_issues" 'BEGIN { printf "%.2f", s/i }')
fi

sc_score=$(printf '%s' "$score" | jq -r '.score // "unavailable"' 2>/dev/null)
sc_score="${sc_score:-unavailable}"
sc_date=$(printf '%s' "$score" | jq -r '.date // "unavailable"' 2>/dev/null)
sc_date="${sc_date:-unavailable}"
deps_count=$(printf '%s' "$deps" | jq -r '.dependentCount // "unavailable"' 2>/dev/null)
deps_count="${deps_count:-unavailable}"

jq -n \
  --arg repo "$REPO" \
  --arg stars "$stars" \
  --arg forks "$forks" \
  --arg watchers "$(printf '%s' "$meta" | jq -r 'if has("subscribers_count") then (.subscribers_count|tostring) else "unavailable" end' 2>/dev/null)" \
  --arg license "$license" \
  --arg archived "$archived" \
  --arg pushed_at "$pushed_at" \
  --arg created_at "$created_at" \
  --arg open_issues "$open_issues" \
  --arg language "$language" \
  --arg description "$description" \
  --arg topics "$topics" \
  --arg star_fork "$ratio_sf" \
  --arg star_issue "$ratio_si" \
  --arg fork_rate_pct "$fork_rate" \
  --arg scorecard_score "$sc_score" \
  --arg scorecard_date "$sc_date" \
  --arg deps_dependents "$deps_count" \
  '{repo: $repo, meta: {stars: $stars, forks: $forks, watchers: $watchers, license: $license, archived: $archived, pushed_at: $pushed_at, created_at: $created_at, open_issues: $open_issues, language: $language, description: $description, topics: ($topics | fromjson? // [])}, star_health: {star_fork_ratio: $star_fork, star_issue_ratio: $star_issue, fork_rate_pct: $fork_rate_pct}, scorecard: {score: $scorecard_score, date: $scorecard_date}, deps_dev: {dependent_count: $deps_dependents}}' \
  > "${OUT:-/dev/stdout}" 2>/dev/null || echo '{"error":"jq output failed"}' > "${OUT:-/dev/stdout}"
