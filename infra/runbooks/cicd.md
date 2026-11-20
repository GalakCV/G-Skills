# Runbook: exposed CI/CD & artifact repositories

1. Run `scripts/cicd_check.py <hosts.txt> payloads/cicd-panels.txt`.
2. `access=UNAUTHENTICATED` is the finding. Escalate autonomously, one read-only step:
   - Jenkins: check `/api/json` for an unauthenticated job list (don't open any job's
     console output).
   - GitLab: check `/api/v4/projects` for unauthenticated project listing.
   - Artifactory/Nexus: check the repository-listing API, don't download an artifact.
   Record counts (N jobs, N projects, N repos) as the severity signal — don't enumerate
   every name if there are hundreds; a representative sample is enough proof.
3. `access=gated` (401/403 landing page) is inventory, not a finding — the system
   exists and is fingerprinted but properly access-controlled. Note it for context
   (e.g., explains an internal hostname seen elsewhere) and move on.
4. Never: log in, try default creds, trigger a build, read full build logs, download
   an artifact, or use any secret an unauthenticated API happens to expose (build logs
   in particular love leaking env vars — if you see one, record "job N's log appears
   to contain a credential, not read" and stop).
5. Why this matters more than a directory-listing bug: CI/CD compromise is usually a
   path to source code, secrets, and sometimes direct deploy access — it's a
   structurally higher-value finding than exposed static files, and it's a surface far
   fewer hunters check systematically.
