# Technique: surface mapping (final inventory)

Goal: turn everything the other phases produced into one complete, annotated inventory
of the attack surface. This is the deliverable the hunter reads to decide where to dig.

## Principle: coverage, not pruning

Do NOT rank hosts into "hot/worth it" vs "ignore" and hand back only the top. That
makes the model throw away surface that was often the real way in. Keep the full list.
Signals **annotate**; they never remove a row. The hunter decides what to attack.

## Build the inventory

One row per live host/endpoint, merging passive-enum + active-discovery + http-probe +
js-recon + content-fuzzing. For each row record, from deterministic tool output only:

- host / URL
- HTTP status as actually observed (200 / 401 / 403 / 301→where / 404 / dead) — never
  assume; a 403 is a real gated resource, not "unavailable"
- title, server, detected tech/framework, CDN/WAF
- how it was found (passive source, brute, JS, fuzz)
- notable signals: auth endpoint, admin path, API base, upload, dev/staging hostname,
  parameterized URL, exposed file hit — as annotations, not a score

## Honesty rules

- Confirmed = a tool observed it this run. Hypothesis = inferred/guessed, label it.
- Never present a hypothesis as confirmed, and never report a host as live without an
  httpx/curl observation backing it (see safety.md).
- If a step didn't run or timed out, say so — don't silently drop its hosts.

## Output

Emit the inventory per output-schema (all hosts, with status + tech + signals +
provenance), then a short "where I'd look first and why" note from the hunter — reasons
tied to concrete observed signals, over the full list, not a pre-filtered subset.
