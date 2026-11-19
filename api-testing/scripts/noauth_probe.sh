#!/usr/bin/env bash
# The no-token test: send GET with NO Authorization header to endpoints the spec says
# require auth. A 200 with real data = broken/missing authentication. Read-only.
#
# SAFETY: pick safe, no-param, low-sensitivity GETs first. On a 200 with data, STOP on
# that endpoint — capture ONE minimal record as proof, do not iterate or pull datasets.
set -uo pipefail
BASE="${1:?base url required}"
LIST="${2:?file of paths to test (one per line) required}"

echo "code size  path"
while read -r p; do
  [ -z "$p" ] && continue
  case "$p" in \#*) continue ;; esac
  # strip a leading "GET " if the line came from the miner
  path="${p#GET }"
  url="${BASE%/}$path"
  out=$(curl -sS -m 12 -A "recon-noauth" -o /dev/null -w '%{http_code} %{size_download}' "$url" 2>/dev/null)
  echo "$out  $path"
  sleep 0.5
done < "$LIST"

cat >&2 <<'NOTE'
[interpret]
 401/403         -> auth enforced (expected). Good.
 200 + real data -> MISSING AUTH. Stop, capture ONE minimal redacted record, report.
 404/405         -> not deployed here / wrong method.
Never iterate IDs, never dump. One unauthorized 200 is the finding.
NOTE
