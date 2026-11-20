---
name: recon
description: Authorized bug bounty web reconnaissance. Maps the attack surface end to end (passive + active-safe) and produces a complete annotated inventory. Coverage, not pruning — the hunter decides. Intrusive follow-ups are gated and live in web-testing/api-testing.
---

# Recon specialist (router)

Authorized web reconnaissance. Given a scope, map the attack surface and return a
complete, annotated inventory of every live, in-scope host. **Coverage, not pruning — the
hunter decides.**

This skill is executable: `skill.yaml` defines the phase workflow, `scripts/` implements
each phase, `runbooks/` holds the human triage, `payloads/` holds the permutation set.
Always obey `safety.md` first.

## Core principles
- **Coverage, not pruning.** Signals annotate; they never discard surface.
- **The hunter decides.** The skill maps; the human chooses what to attack.
- **Confirmed vs hypothesis.** A host is confirmed only when a tool observed it this run.
- **Deterministic truth over vibes.** Status/DNS come from observation, never assumption —
  and tools are self-checked (a resolver that drops known-good hosts is misconfigured).

## Workflow (see skill.yaml)

| Phase | Tier | Script | What it does |
|---|---|---|---|
| passive-enum | passive | `scripts/passive_enum.sh` | subfinder/assetfinder + wayback/gau + CT logs |
| active-discovery | active-safe | `scripts/active_discovery.sh` | permutation + DNS brute (resolvers, not target) |
| http-probe | active-safe | `scripts/http_probe.sh` | httpx liveness + fingerprint, status as observed |
| surface-mapping | passive | `scripts/surface_table.py` | the full annotated inventory → `out/surface.tsv` |

Every candidate flows through `scripts/scope_filter.py` (out-of-scope wins; normalize
before matching). Read `runbooks/triage.md` to interpret the result.

**Tool choice:** `tools.md` is the arsenal — read it before any phase. The scripts are
defaults, not limits: pick the tool that best fits the target, substitute when one is
missing, and log why you chose it.

## Phase cards

### passive-enum
No traffic to the target's web servers — passive sources only. Pipe the domain via stdin
to waybackurls/gau (never inherit the TTY, or they hang). Filter against scope; keep the
full list.

### active-discovery
Naming-grammar permutation (`payloads/permutation-words.txt`) + DNS brute from a SecLists
wordlist, resolved with dnsx at a low rate + retry. Self-check: known-good hosts must
resolve, else the rate is too high — back off. DNS only; no HTTP.

### http-probe
httpx liveness + fingerprint, one root request per host, no redirects off-scope. Record
2xx/401/403/301/404/dead honestly — a 403 is a real gated resource, not "unavailable".
Signals annotate, they do not filter.

### surface-mapping
Merge everything into one row per host: status (as observed), tech, source, and signals
(auth, admin, api, dev/staging, gated) as annotations. Never drop a host. Hand the table
to the hunter.

## Gated next steps (NOT part of recon)
Content fuzzing, route mapping, and API auth testing are intrusive. They live in
`web-testing` / `api-testing` and run only via the harness's gated `explore` command,
after the hunter picks a host from the surface table.
