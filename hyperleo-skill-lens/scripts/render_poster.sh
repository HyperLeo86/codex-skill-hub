#!/bin/bash
# 用法: render_poster.sh <poster.html> <out.png> [width] [height]
# 本地 Chrome headless 渲染 HTML 为 PNG（默认 1200x1600）
set -euo pipefail

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HTML_PATH="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
OUT_PNG="$2"
W="${3:-1200}"
H="${4:-1600}"

if [ ! -x "$CHROME" ]; then
  echo "未找到 Chrome: $CHROME" >&2
  exit 2
fi

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --window-size="$W,$H" --screenshot="$OUT_PNG" "file://$HTML_PATH" >/dev/null 2>&1

echo "$OUT_PNG"
