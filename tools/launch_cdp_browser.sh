#!/usr/bin/env bash
# Launch an isolated headless Chromium with a loopback-only CDP endpoint so
# REA's web tools (inspect_web_page, analyze_web_bundle, capture_web_screenshot)
# can attach to it. Each URL argument is opened in its own tab.
#
# Usage: tools/launch_cdp_browser.sh [--port 9333] URL [URL ...]
# Stop:  pkill -f 'remote-debugging-port=<port>'
set -euo pipefail

port=9333
if [[ "${1:-}" == "--port" ]]; then
  port="$2"
  shift 2
fi
if [[ $# -eq 0 ]]; then
  echo "usage: $0 [--port N] URL [URL ...]" >&2
  exit 2
fi

chromium="${CHROMIUM:-$(command -v chromium || command -v chromium-browser || command -v google-chrome)}"
profile="$(mktemp -d -t rea-cdp-profile.XXXXXX)"

"$chromium" --headless=new --no-first-run --no-default-browser-check \
  --remote-debugging-address=127.0.0.1 --remote-debugging-port="$port" \
  --user-data-dir="$profile" --window-size=1366,900 about:blank \
  >"$profile/chrome.log" 2>&1 &

for _ in $(seq 1 30); do
  curl -s "http://127.0.0.1:$port/json/version" >/dev/null && break
  sleep 1
done

for url in "$@"; do
  curl -s -X PUT "http://127.0.0.1:$port/json/new?$url" >/dev/null
done

# Give pages time to settle, then print target ids for REA's target_id input.
sleep 15
curl -s "http://127.0.0.1:$port/json/list" | python3 -I -c '
import json, sys
for t in json.load(sys.stdin):
    if t["type"] == "page":
        print(t["id"], t["url"], "|", t["title"][:90])
'
echo "CDP endpoint: http://127.0.0.1:$port   profile: $profile"
