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
