# Technique: injection (SQLi, command, SSTI, NoSQL) — safe confirmation

Find where untrusted input reaches an interpreter. Confirm with SAFE, non-destructive
probes — never destructive payloads, never data exfiltration beyond minimal proof.

## Map the inputs
Every parameter, body field, header, cookie, and path segment that reaches a backend
query, shell, template, or NoSQL filter. Prioritize search, filter, sort, id, and
free-text fields.

## SQLi — confirm safely
- **Differential/boolean**: compare a true vs false condition response (`' AND '1'='1`
  vs `' AND '1'='2`) — behavior difference indicates injection without extracting data.
- **Error-based**: a single quote that triggers a DB error reveals the sink. Capture the
  error, don't go further than needed.
- **Time-based (blind)**: a bounded sleep confirms blind injection (keep it short). Do NOT
  dump tables, read files, or stack destructive queries. One confirmation is the finding.

## Command injection
- Safe markers only: a bounded `sleep`/timing probe or a benign echo reflected in the
  response. Never run destructive commands, reverse shells, or anything touching the host
  beyond proving the sink.

## SSTI (template injection)
- Probe with an arithmetic marker (`{{7*7}}`, `${7*7}`) and look for the evaluated result
  (49). Confirm the engine; do not escalate to RCE payloads on a live target without
  explicit approval — the evaluated-expression proof is enough to report.

## NoSQL / operator injection
- Operator payloads in JSON (`{"$ne": null}`, `{"$gt": ""}`) that change auth/filter
  behavior. Confirm the behavior change; don't exfiltrate.

## Confirm & report
- Evidence: the input + the observed differential/error/timing/evaluation. Name the sink
  class and CWE (89/78/1336/943). Note what you did NOT do (no data extraction). Stop at
  proof — the goal is a confirmed, responsibly-demonstrated bug, not a dump.
