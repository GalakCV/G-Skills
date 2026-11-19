#!/usr/bin/env bash
# Active discovery: naming-grammar permutation + DNS brute force, resolution only.
# This is active-SAFE: it queries DNS resolvers, not the target's web servers.
# NO HTTP requests here.
#
# Field lesson: dnsx lies at high rate/threads. Use a low rate + retry>=2, and
# self-check against known-good hosts before trusting a bulk run.
set -uo pipefail
RUN_DIR="${1:?run_dir required}"
WORDLIST="${2:?dns wordlist required}"
RATE="${3:-50}"
HERE="$(cd "$(dirname "$0")" && pwd)"
SCOPE="$RUN_DIR/scope.json"
mkdir -p "$RUN_DIR/raw" "$RUN_DIR/hosts"
RAW="$RUN_DIR/raw"

seeds=$(python3 -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['seeds']))" "$SCOPE")
PERM="$HERE/../payloads/permutation-words.txt"

# Build candidates: wordlist x seeds + permutation of known names from passive.
: > "$RAW/active_candidates_raw.txt"
for d in $seeds; do
  [ -f "$WORDLIST" ] && awk -v d="$d" '{print $1"."d}' "$WORDLIST" >> "$RAW/active_candidates_raw.txt"
done
if [ -f "$RUN_DIR/hosts/passive.txt" ] && [ -f "$PERM" ]; then
  while read -r h; do
    base="${h%%.*}" ; dom="${h#*.}"
    while read -r w; do
      printf '%s-%s.%s\n%s.%s.%s\n%s-%s.%s\n' "$base" "$w" "$dom" "$w" "$base" "$dom" "$w" "$base" "$dom"
    done < "$PERM"
  done < "$RUN_DIR/hosts/passive.txt" >> "$RAW/active_candidates_raw.txt"
fi

sort -u "$RAW/active_candidates_raw.txt" | python3 "$HERE/scope_filter.py" "$SCOPE" > "$RUN_DIR/hosts/active_candidates.txt"

# Self-check: known-good (passive) hosts must resolve at these settings, else back off.
if [ -s "$RUN_DIR/hosts/passive.txt" ]; then
  known=$(head -50 "$RUN_DIR/hosts/passive.txt" | dnsx -silent -rl "$RATE" -retry 2 2>/dev/null | wc -l)
  total=$(head -50 "$RUN_DIR/hosts/passive.txt" | wc -l)
  echo "[*] dnsx self-check: $known/$total known-good resolved (if low, rate too high)" >&2
fi

dnsx -l "$RUN_DIR/hosts/active_candidates.txt" -silent -rl "$RATE" -retry 2 2>/dev/null \
  | awk '{print $1}' | python3 "$HERE/scope_filter.py" "$SCOPE" | sort -u > "$RUN_DIR/hosts/active.txt"

# Merge everything the harness will probe.
cat "$RUN_DIR/hosts/passive.txt" "$RUN_DIR/hosts/active.txt" 2>/dev/null | sort -u > "$RUN_DIR/hosts/all.txt"
echo "[+] active in-scope hosts: $(wc -l < "$RUN_DIR/hosts/active.txt"); total: $(wc -l < "$RUN_DIR/hosts/all.txt")" >&2
