# Safety & hard gates — infra (obey before every phase)

Deterministic rules. Not the agent's to relax.

## 1. Authorization & scope
- Only test in-scope hosts. Out-of-scope always wins. A CNAME that points OFF-scope is not
  followed and attacked — the dangling record on the in-scope host is the finding, not the
  third-party target.

## 2. Detection, never takeover/exploitation
- A dangling CNAME pointing at a claimable service IS the finding. **Never actually claim,
  register, or create the resource** — doing so can disrupt the target and exceeds a
  responsible proof. Report the dangling record + the matched claimable service.
- Exposed panel/service: confirming it's reachable without auth IS the finding. Do NOT log
  in (even with default creds), brute force, or interact with the service beyond the
  read-only request that proves exposure.

## 3. Non-destructive
- Read-only. No config changes, no account creation, no state-changing requests, no DoS.
  Zone transfer (AXFR) only where the program permits.

## 4. Secrets & evidence
- Any credential/key seen is recorded as "exists, location X", redacted — never echoed,
  never used.
- Report only what was observed this run. A takeover candidate is a hypothesis until the
  service fingerprint confirms it's claimable; label it honestly.

## 5. Rate & honesty
- Polite rates. Confirmed = observed this run. Dangling CNAME to a non-claimable service
  (e.g. deleted CloudFront) is a weak signal, not a confirmed takeover — say so.

## 6. Autonomous escalation (active-safe phases only)
- No per-step human approval needed inside an active-safe phase. On a promising signal
  the agent may, on its own: re-confirm, check sibling hosts/environments for the same
  issue, and take one more read-only step to size severity (e.g. count unauth CI jobs,
  check whether an unrelated cert also answers the other way round). Still bounded by
  rules 1-5 — never a login attempt, never a resource claim, never using a found secret.
- The line that always needs `explore`'s human gate: logging into anything (even
  default creds), claiming/registering a dangling resource, submitting a script/job to
  a CI system, downloading an artifact, or sending an AXFR/write-shaped DNS request the
  program hasn't pre-approved.
- On a HIGH-signal finding (claimable dangling CNAME, unauthenticated CI/CD with a real
  job/project list, a cert naming a clearly unrelated company), stop widening the sweep
  on that host/class and surface a draft report immediately rather than waiting for the
  rest of the phase list — the same duplicate-race logic as in cloud/safety.md §6.
