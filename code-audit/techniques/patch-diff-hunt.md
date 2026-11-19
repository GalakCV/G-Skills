# Technique: patch-diff hunt (phase 5, optional) — n-day into 0-day

Goal: security fixes leak information — the diff shows exactly what was wrong. Read a fix
commit (diff + message) and extract (a) the vulnerable pattern that existed *before* the
patch, and (b) a concrete plan to find **variants**: the same mistake elsewhere, an
**incomplete fix**, or the pattern in similar projects. Run when given a fix commit or
hunting variants of a known bug.

## Extract

- **Root cause**: what made the pre-patch code vulnerable (missing check, wrong API,
  bypassable sanitizer).
- **Vulnerable pattern**, abstracted enough to match variants — not just this one file.
- **Incomplete-fix check**: does the patch fully fix it, or can the fix be bypassed
  (wrong layer, one call site patched but not others, blocklist vs allowlist)?
- **Variant hunt plan**: where else the pattern likely appears, plus a concrete
  **Semgrep rule idea** or grep that would surface variants across the codebase. Feed
  that rule back into phase 2 (sast-scan) to actually find them.

## Output (JSON, reasoning_trace first)

```
{"reasoning_trace": "...",
 "root_cause": "user path joined without normalization -> traversal",
 "vulnerable_pattern": "os.path.join(BASE, request-controlled) then open() with no realpath check",
 "fix_complete": false,
 "bypass_idea": "fix strips '../' once; '....//' survives",
 "variant_plan": "grep os.path.join(.*request and open(; check download/export handlers",
 "semgrep_rule_idea": "pattern: open(os.path.join(..., $X)) where $X comes from request",
 "cwe": "CWE-22"}
```

An incomplete fix (`fix_complete: false` with a working bypass) is itself a 0-day — route
it to phase 4 to confirm, then phase 6 to report.
