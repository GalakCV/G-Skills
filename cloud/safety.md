# Safety & hard gates — cloud (obey before every phase)

Deterministic rules. Not the agent's to relax.

## 1. Authorization & ownership
- Only test cloud assets that clearly belong to the in-scope target (named after it, linked
  from it, or in its account per the program scope). A bucket that merely contains the
  target's name but belongs to someone else is OUT OF SCOPE.
- Out-of-scope always wins. Unclear ownership → STOP and ask.

## 2. Detection and reachability ONLY — never exploitation
- Proving public access (a listable bucket, reachable metadata) IS the finding. Stop there.
- **Never retrieve or use cloud credentials.** If metadata exposes IAM credentials, do NOT
  fetch them, do NOT use them, do NOT enumerate the account with them. Report that metadata
  is reachable via the SSRF; that is the vulnerability.
- Never download bucket contents beyond a single minimal proof (the listing response or one
  object name). Never exfiltrate data. Never write, overwrite, or delete any object.

## 3. Non-destructive
- Read-only requests. No PUT/DELETE to storage, no creating resources, no modifying
  configuration, no actions that cost the target money or change state.

## 4. Secrets & evidence
- Any credential/key/token seen (in a bucket, in metadata, in a config) is recorded as
  "exists, location X", redacted. Never echo the value, never forward it to a model, never
  use it.

## 5. Honesty & rate
- Confirmed = a request observed public access this run. Otherwise hypothesis.
- Polite rates. Bucket-name brute force is bounded and low-rate; this is not a mass scanner.

## 6. Autonomous escalation (active-safe phases only)
- The agent does not need a human to approve each step of an active-safe phase. When a
  phase finds something promising, it may on its own: re-confirm the finding, check the
  same misconfig across sibling hosts/environments, and go one read-only step deeper to
  size the blast radius (e.g. count files in a listing, check whether the same console
  is open on dev/qa/stage too). This is still bounded by rules 1-5 above — it never
  becomes a reason to retrieve credentials, claim a resource, or write/delete anything.
- The moment a next step would need a real login attempt, a crafted payload sent to an
  internal/metadata IP, or using something found (a key, a token, a session) — stop and
  hand off to the gated `metadata-reach` phase or to `explore`, which require the
  human's go-ahead per target.
- On a HIGH-signal finding (bucket public-list, console reachable without auth, origin
  IP bypassing the CDN, metadata hypothesis with a very direct param): stop expanding
  the sweep on that host/class and surface the finding immediately with a draft
  report, rather than waiting for the full phase list to finish. Speed to report
  matters as much as depth once something this unambiguous is confirmed.
