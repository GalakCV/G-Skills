---
name: infra
description: Authorized infrastructure attack-surface testing for bug bounty. Finds subdomain takeovers (dangling CNAMEs, ranked by claim-likelihood), exposed admin panels/CI-CD, TLS weaknesses and shared/mismatched certs, and DNS misconfig on in-scope hosts. Most phases are active-safe and run autonomously; claiming a resource or logging into a panel stays gated via explore.
---

# Infra specialist (router)

Test the **infrastructure attack surface** of an authorized, in-scope target: subdomain
takeover, exposed services/admin panels/CI-CD, and TLS/DNS weaknesses. You **detect and
prove safely** — you do NOT claim a dangling resource, log into a panel, or exploit a
service.

Executable: `skill.yaml` defines the workflow, `scripts/` implements checks, `runbooks/`
holds triage, `payloads/` holds takeover fingerprints, panel paths and CI/CD paths. Obey
`safety.md` — including §6, which spells out what you may do without waiting for a
human to approve each step.

## Core principles
- **Detection, not takeover.** Finding a dangling CNAME pointing at a claimable service IS
  the finding. Do NOT actually claim/register the resource — that's the exploitation step
  and can disrupt the target.
- **Dangling ≠ takeover.** A dangling CNAME is only a takeover if the target service is
  claimable. Rank by service (S3/GitHub Pages/Heroku/Azure/Fastly/Pantheon/etc. = high;
  deleted CloudFront = usually not claimable) — see `cname-claim-score` below.
- **Confirmed vs hypothesis.** Confirmed only when a tool observed it this run.
- **Autonomous within active-safe.** No per-step sign-off needed to re-confirm a finding,
  check sibling hosts/environments, or size severity with one more read-only step — only
  a login attempt, a resource claim, or using a found secret needs `explore`'s human gate.

## Workflow (see skill.yaml)

| Phase | Tier | Card | What it does |
|---|---|---|---|
| takeover | active-safe | `runbooks/takeover.md` | dangling CNAME → match takeover-prone service fingerprint |
| cname-claim-score | active-safe | `runbooks/cname-score.md` | rank takeover's output by claim-likelihood so the 2-3 real candidates don't drown in dead-CloudFront noise |
| exposed-services | active-safe | `runbooks/services.md` | admin panels, dev tools, management UIs reachable |
| cicd-exposure | active-safe | `runbooks/cicd.md` | exposed Jenkins/GitLab/Artifactory/Nexus/TeamCity reachable without auth |
| tls | active-safe | `runbooks/tls.md` | expired/mismatched certs, weak protocols |
| shared-cert | active-safe | `runbooks/shared-cert.md` | a cert naming an unrelated third-party domain — tenant/host confusion |
| dns | active-safe | `runbooks/dns.md` | zone transfer, dangling records, misconfig |

## Phase cards (summary)

### takeover (highest value)
From recon's hosts: resolve CNAMEs. A host whose CNAME target does NOT resolve (or returns
the service's "no such bucket/app" fingerprint) is a takeover candidate. Match the target
against `payloads/takeover-fingerprints.txt`. Report the dangling CNAME + the matched
service + whether it's claimable — but NEVER register/claim it. (Lesson: deleted CloudFront
distributions are usually NOT trivially claimable; S3/GitHub Pages/Heroku/Azure are.)

### cname-claim-score
Pure classification of `takeover`'s own output — no new network requests. Buckets results
into CLAIMABLE / UNKNOWN / NOT-CLAIMABLE so a 187-CNAME sweep doesn't bury the 2-3 real
candidates in dead-CloudFront noise. Always active-safe; run it every time.

### exposed-services
Probe in-scope hosts for reachable admin panels, dev tools, and management UIs (Grafana,
Kibana, phpMyAdmin, Actuator, .git, etc.) with read-only GETs. Reachable + no auth =
finding. Do NOT log in, brute force, or interact beyond confirming exposure.

### cicd-exposure
Probe for Jenkins/GitLab/Artifactory/Nexus/TeamCity/Bamboo/Drone/Argo CD reachable without
auth. A real job/project/repo list observed unauthenticated is the finding — record a
count, don't enumerate everything; never read full build logs or download artifacts.

### tls
Check certs for expiry, hostname mismatch, and weak protocol/cipher support (read-only,
openssl-style). Report the weakness; this is low severity unless it enables something.

### shared-cert
Flags a host whose live certificate names a clearly unrelated third-party domain — a
signal of shared infrastructure / tenant bleed-through, not just a cert hygiene nitpick.
Never test the foreign domain itself beyond confirming it's unrelated.

### dns
Attempt AXFR zone transfer (if the program allows), look for dangling/stale records and
obvious DNS misconfig. Detection only.
