#!/usr/bin/env bash
# Read-only TLS check: expiry, hostname match, protocol support. No exploitation.
# Usage: tls_check.sh <host> [port]
set -uo pipefail
HOST="${1:?host required}"; PORT="${2:-443}"
echo "== $HOST:$PORT =="
# cert dates + subject/SAN
echo | timeout 12 openssl s_client -connect "$HOST:$PORT" -servername "$HOST" 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates -ext subjectAltName 2>/dev/null \
  || echo "[!] could not retrieve certificate"
# weak protocols (report if they connect)
for proto in -ssl3 -tls1 -tls1_1; do
  if echo | timeout 8 openssl s_client -connect "$HOST:$PORT" -servername "$HOST" "$proto" 2>/dev/null | grep -q "BEGIN CERTIFICATE"; then
    echo "WEAK: $proto accepted"
  fi
done
