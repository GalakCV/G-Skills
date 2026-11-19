# Technique: SAST triage (phase 3) — the harness's main job

Goal: judge each finding as **true positive vs false positive** from its sink slice +
pulled definitions. SAST is noisy; most hits are FPs (test code, sanitized input,
non-exploitable patterns). Be strict — a clean list of TPs beats a long list that
buries them. Run temperature 0.

## How to judge (in order)

1. **Is untrusted input reachable here?** Constant, hardcoded config, test fixture, or
   developer-controlled value at the sink → false positive (or informational).
2. **Is it sanitized/validated before the sink?** Parameterized query, escaping,
   allowlist, neutralizing type coercion → false positive.
3. **Is the sink dangerous as actually called?** e.g. `subprocess.run([...])` without
   `shell=True` and a list arg is usually safe; `yaml.safe_load` ≠ `yaml.load`.
4. **Context**: test/mock/example code → lower to FP or info.

If you can't tell from the slice whether a source reaches the sink, return
`needs_review` with what else you'd need — do NOT guess `true_positive`.

## Output (JSON, reasoning_trace first)

```
{"reasoning_trace": "...",
 "verdict": "true_positive | false_positive | needs_review",
 "confidence": 0-100,
 "cwe": "CWE-89",
 "severity": "critical|high|medium|low|info",
 "title": "SQL injection in UserRepo.find via f-string query",
 "why": "request.args['id'] flows unsanitized into cursor.execute f-string",
 "next_step": "confirm source: trace id param from route to this call"}
```

Only `true_positive` and `needs_review` survivors go to phase 4 (dataflow). Drop the FPs.
