#!/usr/bin/env bash
# Passive enumeration. No direct traffic to the target's web servers — only
# passive sources (subfinder APIs, CT logs, archive data). Reads seeds from
# $RUN_DIR/scope.json, writes in-scope hosts to $RUN_DIR/hosts/passive.txt.
#
# Field lesson: waybackurls/gau read stdin and hang forever if stdin is a TTY.
# Always pipe the domain in via echo; never leave stdin inherited.
set -uo pipefail
RUN_DIR="${1:?run_dir required}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCOPE="$RUN_DIR/scope.json"
mkdir -p "$RUN_DIR/raw" "$RUN_DIR/hosts"
RAW="$RUN_DIR/raw"

seeds=$(python3 -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['seeds']))" "$SCOPE")

: > "$RAW/passive_all.txt"
for d in $seeds; do
  echo "[*] passive: $d" >&2
  timeout 600 subfinder -d "$d" -silent -all               2>/dev/null >> "$RAW/passive_all.txt"
  timeout 180 assetfinder --subs-only "$d"                 2>/dev/null >> "$RAW/passive_all.txt"
  echo "$d" | timeout 300 waybackurls 2>/dev/null | sed -E 's#^[a-z]+://##;s#[/:].*##' >> "$RAW/passive_all.txt"
  echo "$d" | timeout 300 gau --subs  2>/dev/null | sed -E 's#^[a-z]+://##;s#[/:].*##' >> "$RAW/passive_all.txt"
  # CT logs (passive): crt.sh + certspotter
  curl -sS -m 60 "https://crt.sh/?q=%25.$d&output=json" 2>/dev/null \
    | python3 -c "import sys,json;[print(n) for r in (json.load(sys.stdin) or []) for n in r.get('name_value','').split(chr(10))]" 2>/dev/null \
    >> "$RAW/passive_all.txt" || true
done

sort -u "$RAW/passive_all.txt" | python3 "$HERE/scope_filter.py" "$SCOPE" | sort -u > "$RUN_DIR/hosts/passive.txt"
echo "[+] passive in-scope hosts: $(wc -l < "$RUN_DIR/hosts/passive.txt")" >&2
