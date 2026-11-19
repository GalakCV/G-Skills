---
name: cloud
description: Authorized cloud attack-surface testing for bug bounty. Finds exposed storage buckets, misconfigured cloud assets, and metadata reachability tied to in-scope targets. Detection and reachability proof only — never retrieves or uses real cloud credentials. Intrusive; runs via the gated explore command.
---

# Cloud specialist (router)

Test the **cloud attack surface** of an authorized, in-scope target: exposed object
storage, misconfigured cloud assets, and cloud-metadata reachability. You **detect and
prove reachability** — you do NOT steal credentials, exfiltrate data, or modify anything.

Executable: `skill.yaml` defines the workflow, `scripts/` implements checks, `runbooks/`
holds triage, `payloads/` holds bucket-name permutations. Obey `safety.md` first.

## Core principles
- **Detection, not exploitation.** Proving a bucket is publicly listable, or that metadata
  is reachable, is the finding. Stop there — never pull credentials or dump data.
- **Tie to the in-scope target.** Only test buckets/assets clearly belonging to the target
  (named after it, linked from it, or in its cloud account per the program).
- **Confirmed vs hypothesis.** A bucket is exposed only when a request observed public
  access this run.

## Workflow (see skill.yaml)

| Phase | Card | What it does |
|---|---|---|
| asset-fingerprint | `runbooks/fingerprint.md` | detect provider (AWS/GCP/Azure) from CNAME/headers/IP |
| bucket-exposure | `runbooks/buckets.md` | find & test object storage for public list/read |
| metadata-reach | `runbooks/metadata.md` | is cloud metadata reachable (via an SSRF found in web-testing)? |
| misconfig | `runbooks/misconfig.md` | public snapshots, open dashboards, exposed cloud services |

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

### metadata-reach
Cloud metadata (169.254.169.254 and provider variants) is only reachable through an SSRF.
If web-testing confirmed an SSRF, note whether it reaches metadata — but STOP at
reachability. Do NOT retrieve or use IAM credentials from metadata; that is exploitation
and data theft.

### misconfig
Public EBS/RDS snapshots, open storage browsers, exposed cloud management dashboards tied
to the target. Detection + reachability proof only.
