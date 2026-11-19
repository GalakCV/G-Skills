#!/usr/bin/env bash
# HTTP liveness + fingerprint. Active-SAFE: one root request per host. No path
# fuzzing, no auth, no following redirects off-scope. Records the status exactly
# as observed (200/401/403/301/404/dead).
set -uo pipefail
RUN_DIR="${1:?run_dir required}"
RATE="${2:-10}"
mkdir -p "$RUN_DIR/out"
LIST="$RUN_DIR/hosts/all.txt"
[ -s "$LIST" ] || { echo "[!] no hosts to probe" >&2; exit 0; }

httpx -l "$LIST" -silent -json \
  -sc -title -td -location -cname -cdn -ip -webserver -no-color \
  -rl "$RATE" -t 20 -timeout 12 -retry 1 \
  -o "$RUN_DIR/out/httpx.jsonl" 2>/dev/null

# Dead = in all.txt but produced no httpx record (DNS fail / refused / timeout).
python3 - "$LIST" "$RUN_DIR/out/httpx.jsonl" "$RUN_DIR/out/dead.txt" <<'PY'
import sys,json
allh=set(l.strip() for l in open(sys.argv[1]) if l.strip())
live=set()
try:
    for line in open(sys.argv[2]):
        if line.strip():
            live.add(json.loads(line).get("input","").strip())
except FileNotFoundError:
    pass
open(sys.argv[3],"w").write("\n".join(sorted(allh-live)))
print(f"[+] probed: {len(live)} live, {len(allh-live)} dead", file=sys.stderr)
PY
