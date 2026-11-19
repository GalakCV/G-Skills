---
name: infra
description: Authorized infrastructure attack-surface testing for bug bounty. Finds subdomain takeovers (dangling CNAMEs), exposed admin panels and services, and TLS/DNS weaknesses on in-scope hosts. Detection and safe proof only — never claims the resource or exploits the service. Intrusive; runs via the gated explore command.
---

# Infra specialist (router)

Test the **infrastructure attack surface** of an authorized, in-scope target: subdomain
takeover, exposed services and admin panels, and TLS/DNS weaknesses. You **detect and
prove safely** — you do NOT claim a dangling resource, log into a panel, or exploit a
service.

Executable: `skill.yaml` defines the workflow, `scripts/` implements checks, `runbooks/`
holds triage, `payloads/` holds takeover fingerprints and panel paths. Obey `safety.md`.

## Core principles
- **Detection, not takeover.** Finding a dangling CNAME pointing at a claimable service IS
  the finding. Do NOT actually claim/register the resource — that's the exploitation step
  and can disrupt the target.
- **Dangling ≠ takeover.** A dangling CNAME is only a takeover if the target service is
  claimable. Rank by service (S3/GitHub Pages/Heroku/Azure/Fastly = high; deleted
  CloudFront = usually not claimable).
- **Confirmed vs hypothesis.** Confirmed only when a tool observed it this run.

## Workflow (see skill.yaml)

| Phase | Card | What it does |
|---|---|---|
| takeover | `runbooks/takeover.md` | dangling CNAME → match takeover-prone service fingerprint |
| exposed-services | `runbooks/services.md` | admin panels, dev tools, management UIs reachable |
| tls | `runbooks/tls.md` | expired/mismatched certs, weak protocols |
| dns | `runbooks/dns.md` | zone transfer, dangling records, misconfig |

## Phase cards (summary)

### takeover (highest value)
From recon's hosts: resolve CNAMEs. A host whose CNAME target does NOT resolve (or returns
the service's "no such bucket/app" fingerprint) is a takeover candidate. Match the target
against `payloads/takeover-fingerprints.txt`. Report the dangling CNAME + the matched
service + whether it's claimable — but NEVER register/claim it. (Lesson: deleted CloudFront
distributions are usually NOT trivially claimable; S3/GitHub Pages/Heroku/Azure are.)

### exposed-services
Probe in-scope hosts for reachable admin panels, dev tools, and management UIs (Jenkins,
Grafana, Kibana, phpMyAdmin, Actuator, .git, etc.) with read-only GETs. Reachable + no auth
= finding. Do NOT log in, brute force, or interact beyond confirming exposure.

### tls
Check certs for expiry, hostname mismatch, and weak protocol/cipher support (read-only,
openssl-style). Report the weakness; this is low severity unless it enables something.

### dns
Attempt AXFR zone transfer (if the program allows), look for dangling/stale records and
obvious DNS misconfig. Detection only.
