# Technique: SAST scan + context slicing (phase 2)

Goal: locate candidate vulnerabilities deterministically with Semgrep (and CodeQL when
available), then pull the code slice each candidate needs for triage. The engine finds;
it does NOT judge.

## Run Semgrep (always)

- `semgrep --config auto --json <repo>` for a broad first pass, or `--config p/<lang>`
  / a curated ruleset targeting the sink classes from phase 1.
- Respect the file scope filter in safety.md — point Semgrep at application code, skip
  vendor/test/minified. Use `--exclude` for dirs the engine doesn't skip itself.
- Semgrep analyzes source without executing it. Never run the app to "check".

## Run CodeQL (if present — degrade gracefully)

- CodeQL adds real dataflow/taint and variant analysis. If the `codeql` CLI and a DB
  build are available, run the relevant query pack for the language.
- If CodeQL is NOT installed, do not block — note `codeql: unavailable` and proceed on
  Semgrep + manual dataflow reasoning (phase 4). State the reduced confidence.

## Context slicing (for each candidate)

For every finding, pull a focused, redacted slice so triage can judge without the whole
repo:
- the sink line plus ~15 lines around it
- the enclosing function
- the definitions of functions called on the tainted value's path (one hop out)
Redact secrets in the slice before it reaches any model (safety.md §4).

## Output

A list of candidates, each with: rule id, message, file:line, CWE guess, and the sliced
+ redacted context. Do not label any of them true/false positive here — that is the
triage phase's job. Hand the list to `sast-triage`.
