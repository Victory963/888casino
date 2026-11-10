#!/usr/bin/env bash
# Run REA's static JavaScript application reconstruction on a local directory
# of downloaded bundles (plus any *.map files next to them) and keep both the
# summary view and the complete Evidence bundle.
#
# Usage: tools/run_rea_js_analysis.sh APP_DIR OUT_PREFIX
#   -> OUT_PREFIX.summary.json, OUT_PREFIX.json (complete Evidence), OUT_PREFIX.err (progress log)
#
# The CLI is used instead of the MCP tool on purpose: after an in-place REA
# upgrade a still-running MCP server can mismatch its analysis workers.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 APP_DIR OUT_PREFIX" >&2
  exit 2
fi
app_dir="$(cd "$1" && pwd)"
out="$2"

rea analyze-javascript-application "$app_dir" \
  --artifact-format directory \
  --detail summary \
  --evidence_output "$out.json" \
  --max-heap-mb 3072 \
  --analysis-timeout-ms 1200000 \
  --format json >"$out.summary.json" 2>"$out.err"

echo "summary:  $out.summary.json"
echo "evidence: $out.json"
