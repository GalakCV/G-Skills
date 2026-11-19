# Technique: reporting (phase 6) — confirmed finding → write-up

Goal: for a finding triage + dataflow agree is `exploitable`, produce the write-up a
maintainer or a CVE / bug-bounty submission needs: precise, reproducible, actionable.
Sanity-check the claim one last time — if the evidence doesn't actually support
exploitability, downgrade it honestly rather than overstate.

## Produce

- **Title & severity** with CVSS-style *reasoning* — not a faked exact score.
- **Root cause**: the precise flaw, in plain technical language.
- **Impact**: what the attacker achieves (RCE, data read, auth bypass…) and
  preconditions (auth required? specific config?).
- **Proof of concept**: a concrete request/input/sequence that triggers it. Describe a
  minimal, responsible repro — do NOT include working exploit payloads for destructive
  actions (safety.md §1).
- **Remediation**: the specific code fix (parameterize, validate, safe API) and the
  secure pattern to adopt.
- **Honest confidence**: if a step is unverified (e.g. source reachability not confirmed
  without running the code), say so.

## Output (JSON, reasoning_trace first)

```
{"reasoning_trace": "...",
 "title": "Unauthenticated SQL injection in /api/search",
 "severity": "high",
 "cwe": "CWE-89",
 "root_cause": "search() builds SQL with an f-string from request.args['q']",
 "impact": "read arbitrary DB rows; no auth required",
 "preconditions": "none; public endpoint",
 "poc": "GET /api/search?q=' OR '1'='1 -> returns all rows (responsible repro)",
 "remediation": "use parameterized query: cursor.execute(SQL, (q,))",
 "confidence": 80,
 "caveats": "source reachability confirmed from route; not run live"}
```

This is the final artifact. Only confirmed (or honestly-labeled needs_review) findings
appear in it — never the raw SAST list.
