# Runbook: reading the surface table

After `recon`, `out/surface.tsv` holds the full inventory. This runbook is how a human
reads it and decides where to dig. No tool decides what's worth attacking — you do.

## Principle: coverage, not pruning
Every live/in-scope host is a row. Signals annotate; they never remove a row. Do not let
the list be filtered down to a "hot" subset — the way in is often a host a ranker would
have dropped.

## How to read a row
- **status** — exactly as observed. A `403`/`401` is a real gated resource (keep it, it's
  often more interesting than a `200`). `dead` means no HTTP response this run (DNS fail /
  refused / timeout) — not "ignore", just not reachable now.
- **signals** — annotations, in priority order to eye-scan:
  - `dev/staging` — weaker controls, debug on, test data. High priority.
  - `api` — likely a REST/GraphQL surface → candidate for `api-testing` (gated explore).
  - `auth` / `admin` — login, SSO, admin panels → access-control and auth testing.
  - `gated` (401/403) — a resource that exists but is protected → probe authorization.

## What to confirm before claiming anything
- `state` is `confirmed` only because a tool observed the host this run. A finding ON that
  host still needs its own confirmation — confirmed host ≠ confirmed vulnerability.
- Never report a host as live without the httpx/curl observation backing it.

## Where to go next (all gated — run via the harness `explore` command)
1. A `dev/staging` + `api` host → `api-testing`: find the spec, test auth enforcement
   (no-token GET), then BOLA/BFLA.
2. An `auth`/`admin` host → `web-testing/access-control`: IDOR, missing authz, the
   incomplete-fix pattern.
3. A rich `200` web app → `web-testing`: injection, SSRF, XSS (with the CSP reality check),
   file upload (watch MIME normalization on the server).
4. Only after choosing a host → content fuzzing with the right wordlist for its stack.

Pick one host, confirm one thing, report it with minimal evidence. Don't fan out.
