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
