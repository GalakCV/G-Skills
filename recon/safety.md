# Safety — hard gates (read before any recon action)

These are non-negotiable. Violating scope or rate limits can get the hunter removed
from a program or cross a legal line. When unsure, STOP and ask the human.

## Scope (hard gate)

- Act ONLY on hosts that match an `in_scope` pattern AND do not match any
  `out_of_scope` pattern. Out-of-scope ALWAYS wins over in-scope.
- Before running any tool or probe against a host, verify it against the scope. A
  host you cannot confirm is in scope is treated as out of scope — do not touch it.
- Wildcards: `*.example.com` matches `example.com` and any subdomain. Honor the exact
  patterns the scope gives; do not broaden them.
- Never follow a redirect out of scope and keep probing it.

## Rate limiting (hard gate)

- Respect the program's stated rate limit. If none is stated, stay conservative
  (a few requests/second per host). Many programs cap automated traffic (e.g. 3–10
  req/s) — obey the scope's number.
- Do not launch large fan-out scans without the human's go-ahead.

## Active vs passive

- Passive enumeration and light liveness probing are fine within scope + rate limits.
- Anything intrusive — aggressive fuzzing, brute force, authenticated testing,
  anything that writes/changes state — requires explicit human approval first. Ask.
- Never generate or run an exploit. Recon maps surface; it does not attack.

## Secrets

- Never send credentials, cookies, session tokens, or API keys to any model or
  external service. If the scope defines custom session headers, those values stay
  out of any prompt or log — redact them.

## Honesty

- Report only what a tool/probe actually returned. Never invent a host, a status, or
  an endpoint. "Unconfirmed" and "dead/404" are valid, useful answers.
