---
name: cloud
description: Authorized cloud attack-surface testing for bug bounty. Finds exposed storage buckets, exposed cloud-native admin consoles, CDN origin leaks, SSRF-to-metadata hypotheses, and metadata reachability tied to in-scope targets. Most phases are active-safe and run autonomously; claiming/using credentials stays gated via explore.
---

# Cloud specialist (router)

Test the **cloud attack surface** of an authorized, in-scope target: exposed object
storage, exposed admin consoles, CDN origin leaks, misconfigured cloud assets, and
cloud-metadata reachability. You **detect and prove reachability** — you do NOT steal
credentials, exfiltrate data, or modify anything.

Executable: `skill.yaml` defines the workflow, `scripts/` implements checks, `runbooks/`
holds triage, `payloads/` holds bucket-name/console/metadata fingerprints. Obey
`safety.md` first — including §6, which spells out what you may do without waiting for
a human to approve each step.

## Core principles
- **Detection, not exploitation.** Proving a bucket is publicly listable, a console is
  reachable, or that metadata is reachable, is the finding. Stop there — never pull
  credentials, log in, or dump data.
- **Tie to the in-scope target.** Only test buckets/assets clearly belonging to the target
  (named after it, linked from it, or in its cloud account per the program).
- **Confirmed vs hypothesis.** A bucket/console is exposed only when a request observed
  public access this run.
- **Autonomous within active-safe.** You don't need per-step sign-off to re-confirm a
  finding, check sibling hosts/environments, or take one more read-only step to size
  severity — only crossing into login/claim/credential-use needs `explore`'s human gate.

## Workflow (see skill.yaml)

| Phase | Tier | Card | What it does |
|---|---|---|---|
| asset-fingerprint | active-safe | `runbooks/fingerprint.md` | detect provider (AWS/GCP/Azure) from CNAME/headers/IP |
| bucket-exposure | active-safe | `runbooks/buckets.md` | find & test object storage for public list/read |
| admin-console | active-safe | `runbooks/admin-console.md` | exposed Kubernetes dashboard, Azure Kudu/SCM, Actuator, Grafana/Kibana/pgAdmin, etc. |
| cdn-origin-leak | active-safe | `runbooks/cdn-origin.md` | origin IP reachable directly, bypassing the CDN/WAF |
| ssrf-surface | active-safe | `runbooks/iam-surface.md` | flag URL-fetching params as metadata-SSRF hypotheses (no payload sent) |
| metadata-reach | active-intrusive (gated) | `runbooks/metadata.md` | actually probe metadata reachability via a confirmed SSRF |
| misconfig | active-safe | `runbooks/misconfig.md` | public snapshots, open dashboards, exposed cloud services |

## Phase cards (summary)

### asset-fingerprint
From recon's hosts: resolve CNAMEs and read headers to label each as AWS (`s3`,
`cloudfront`, `elb`, `amazonaws`), GCP (`storage.googleapis`, `appspot`), or Azure
(`blob.core.windows`, `azurewebsites`). This decides which bucket/asset checks apply.

### bucket-exposure
Generate candidate bucket names from the target (payloads/bucket-words.txt) for the right
provider, then test each for **public listing / public read** with an unauthenticated GET.
A public, listable bucket owned by the target is the finding — record the URL and a minimal
proof (the listing XML / one object name), never download the contents.

### admin-console
Checks for exposed cloud-native management surfaces (Kubernetes dashboard/API, Azure
Kudu/SCM, Spring Boot Actuator, Grafana/Kibana/Consul/Portainer/pgAdmin). Reachability
without a login attempt is the finding; see `safety.md` §2/§6 for exactly what counts
as safe escalation (checking sibling environments) vs. gated (any login attempt).

### cdn-origin-leak
Compares DNS/cert/history data to find a real origin IP answering directly for a
CDN-fronted host, meaning the CDN/WAF can be bypassed entirely for that host.

### ssrf-surface
Pure static analysis of the param inventory already collected by recon — flags
URL-fetching parameters as hypotheses. Sends nothing to an internal IP; feeds the
gated `metadata-reach` phase.

### metadata-reach
Cloud metadata (169.254.169.254 and provider variants) is only reachable through an SSRF.
If `ssrf-surface` flagged a strong candidate and a human approves testing it, note whether
it reaches metadata — but STOP at reachability. Do NOT retrieve or use IAM credentials
from metadata; that is exploitation and data theft.

### misconfig
Public EBS/RDS snapshots, open storage browsers, exposed cloud management dashboards tied
to the target. Detection + reachability proof only.
