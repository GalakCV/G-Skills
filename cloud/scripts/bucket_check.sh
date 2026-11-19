#!/usr/bin/env bash
# Test candidate object-storage buckets for PUBLIC listing/read. Unauthenticated,
# read-only GET only. A public listable bucket owned by the target is the finding —
# record the URL + minimal proof; never download contents, never write/delete.
#
# Usage: bucket_check.sh <target-name> <run_dir>
set -uo pipefail
NAME="${1:?target name required, e.g. example}"
RUN_DIR="${2:?run_dir required}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORDS="$HERE/../payloads/bucket-words.txt"
OUT="$RUN_DIR/cloud"; mkdir -p "$OUT"
RES="$OUT/buckets.txt"; : > "$RES"

check() { # url
  code=$(curl -sS -m 10 -A "recon-bucket" -o /dev/null -w '%{http_code}' "$1" 2>/dev/null)
  # 200 on a list endpoint = public listing; 403 = exists but private; 404 = none
  if [ "$code" = "200" ]; then echo "PUBLIC  $1" | tee -a "$RES"
  elif [ "$code" = "403" ]; then echo "EXISTS  $1" | tee -a "$RES"; fi
}

while read -r w; do
  case "$w" in ''|\#*) continue ;; esac
  b="${w//\{name\}/$NAME}"
  # AWS S3, GCS, Azure Blob — list-style URLs, read-only
  check "https://$b.s3.amazonaws.com/"
  check "https://storage.googleapis.com/$b/"
  check "https://$b.blob.core.windows.net/?comp=list"
done < "$WORDS"

echo "[+] results -> $RES (PUBLIC = listable; EXISTS = present but private)" >&2
cat >&2 <<'NOTE'
[interpret] A PUBLIC bucket owned by the target: record the URL + the listing response as
proof, then STOP. Do not download objects, do not write, do not delete.
NOTE
