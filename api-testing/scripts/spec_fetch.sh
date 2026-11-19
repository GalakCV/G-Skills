#!/usr/bin/env bash
# Find and fetch an API's own spec (OpenAPI/Swagger). Read-only GETs to common paths.
# Writes any JSON spec found to $RUN_DIR/api/spec_<n>.json for the miner.
set -uo pipefail
BASE="${1:?base url required, e.g. https://api.example.com}"
RUN_DIR="${2:?run_dir required}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$RUN_DIR/api"
PATHS="$HERE/../payloads/spec-paths.txt"

i=0
while read -r p; do
  [ -z "$p" ] && continue
  case "$p" in \#*) continue ;; esac
  url="${BASE%/}$p"
  body=$(curl -sS -m 12 -A "recon-spec" "$url" 2>/dev/null)
  # keep it only if it looks like an OpenAPI/Swagger JSON
  if printf '%s' "$body" | grep -qE '"(openapi|swagger)"\s*:'; then
    i=$((i+1))
    printf '%s' "$body" > "$RUN_DIR/api/spec_$i.json"
    echo "[+] spec found: $url -> api/spec_$i.json" >&2
  fi
done < "$PATHS"
[ "$i" -eq 0 ] && echo "[*] no JSON spec at common paths (try /graphql introspection, JS bundles)" >&2
exit 0
