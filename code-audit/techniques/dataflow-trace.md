# Technique: dataflow trace (phase 4) — confirm the taint path

Goal: for a survivor the triage flagged `true_positive` or `needs_review`, decide
whether a **taint path actually exists**: does attacker-controlled input reach the sink,
and does anything neutralize it on the way? You get the sink slice plus the redacted
definitions of the functions in the call chain. Run temperature 0.

## Reason about the path explicitly

- **Source**: name the concrete attacker-controlled entry (route param, body field,
  header, uploaded filename, request-derived env, etc.).
- **Propagation**: follow the value through the calls shown. Note each hop (assignment,
  function arg, return) carrying the taint toward the sink.
- **Sanitizers**: identify anything that breaks exploitability — escaping,
  parameterization, allowlist/validation, encoding, neutralizing type conversion. A
  real sanitizer on the path means NOT exploitable.
- **Sink**: confirm the dangerous operation and how the tainted value is used.

If the provided slices don't contain a hop you need, put it in `missing` and return
`needs_review` — never fabricate a path you can't see.

## Output (JSON, reasoning_trace first)

```
{"reasoning_trace": "...",
 "verdict": "exploitable | not_exploitable | needs_review",
 "confidence": 0-100,
 "source": "request.json['template']",
 "path": ["view render() -> helper build() -> engine.from_string(sink)"],
 "sanitizers": [],
 "sink": "Jinja2 from_string on attacker input -> SSTI",
 "cwe": "CWE-1336",
 "missing": ""}
```

Only `exploitable` findings go to reporting as confirmed. `needs_review` is reported
honestly as unconfirmed, with what's missing.
