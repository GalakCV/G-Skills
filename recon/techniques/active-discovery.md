# Technique: active discovery (permutation + DNS brute)

Goal: find the hosts passive enumeration missed — the internal/dev/api hosts that never
hit public sources. This is active DNS (resolution only, no HTTP) — low risk, but still
inside scope and rate limits (see safety.md).

## Reason from the naming grammar first (don't brute blindly)

Study the subdomains passive already found and infer the org's pattern, then target it:

- Environment tags: if you see `alpha.`, `beta.`, `gamma.`, `dev.`, `staging.` of an
  app, the siblings (`prod`, `uat`, `sandbox`, `qa`, `canary`) of the SAME app likely
  exist. Generate those.
- Product/suffix patterns: `app` and `app-nutrition` → apply the `-<product>` suffix
  elsewhere.
- Service hints: a SPA that calls an API (an `apiUrl` / `/api/v1` seen in JS) implies
  an `api.<app>` / `<app>-api` host passive missed — target it. Often the highest-value
  host and the main reason to do this phase.
- Function tokens: `admin`, `internal`, `gateway`, `auth`, `sso`, `portal`, `vpn`,
  `git`, `jenkins`, `grafana` — include the ones that fit what you've seen.

## Execute

1. Generate candidates = (known subs × targeted tokens, as prefix/suffix/infix) +
   (a DNS wordlist × apex domains). Keep the candidate count bounded.
   - DNS wordlists (SecLists): start small — `Discovery/DNS/subdomains-top1million-5000.txt`;
     go larger only if the surface is clearly rich.
2. Mass-resolve with `dnsx -silent` (feed candidates on stdin). Keep ONLY the ones that
   resolve AND are in scope.
3. Add the new resolved hosts to the inventory for probing.

## Notes

- No dnsx = skip this phase (without resolution, permutation candidates are just noise).
- Permutation still works without a wordlist; the wordlist only adds brute reach.
