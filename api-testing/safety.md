# Safety & hard gates — API testing (obey before every test)

Deterministic rules. Not the agent's to relax.

## 1. Authorization & scope
- Test only in-scope APIs of an authorized program. Out-of-scope always wins. Unclear
  scope → STOP and ask.

## 2. Read-first, non-destructive
- GET and safe reads before anything that changes state. Never fire POST/PUT/PATCH/DELETE
  blindly against a live API — those create, modify, or delete real data.
- To test write-side authz, prefer your own test objects. Never modify or delete another
  user's or production data to prove a bug.

## 3. Data minimization
- When an endpoint returns data it shouldn't, capture ONE minimal, redacted record as
  proof and stop. Never iterate IDs at scale, paginate through a dataset, or exfiltrate
  real PII. A single unauthorized object proves BOLA; a single no-token 200 proves missing
  auth.

## 4. No credential attacks
- No credential stuffing, no token brute force, no using another real user's token.
- Testing missing auth by sending NO `Authorization` header is fine. Attacking the auth
  server / token issuance itself is not.

## 5. Secrets & redaction
- Never forward tokens, keys, or secrets found in responses/specs to any model. Redact
  before recording. An exposed secret/token in a spec or response is a finding — report its
  existence with the value redacted; never use it to access more.

## 6. Rate & politeness
- Low request rates. No bulk automated fuzzing where the program forbids it. Intrusive or
  high-volume testing needs explicit human approval.

## 7. Honesty
- Confirmed = observed this run. Otherwise `needs_review` with the test that would confirm.
- An exposed spec with all endpoints returning 401 is auth working — report the spec
  exposure as info at most, not as a breach.
