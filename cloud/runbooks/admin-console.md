# Runbook: exposed cloud-native admin consoles

1. Run after `asset-fingerprint` so you know the provider (Azure/GCP/AWS/self-hosted
   Kubernetes) and can skip irrelevant fingerprints.
2. Run `scripts/admin_console_check.py <hosts.txt> payloads/admin-console-fingerprints.txt`.
3. On a hit:
   - `HIGH` note (Kubernetes Dashboard, unauth K8s API, Kudu/SCM, Spring Actuator
     `/env`/`/heapdump`, pgAdmin): this is the finding by itself — a reachable
     management plane. Capture the landing page/response headers as proof. **Do not
     click into the UI, do not run any action inside it, do not browse Actuator's
     `/env` or `/heapdump` contents — their reachability is the bug, their contents
     may be out of scope to read.**
   - `MED` note (Grafana/Kibana/Consul/RabbitMQ/Portainer login pages): reachability
     without a login attempt is a lower-severity finding (info disclosure via
     service fingerprinting) unless the dashboard itself is unauthenticated past the
     landing page. **Never attempt login, never try default credentials
     (admin/admin, guest/guest) — that crosses into active-intrusive and needs the
     explore gate.**
4. Escalation allowed autonomously (active-safe): if a console answers on one host in
   an environment ladder (dev/qa/stage), check the sibling environments
   (same apex, different env prefix) for the same exposure — this is still read-only
   fingerprinting, not deeper exploitation, and it's exactly the kind of "confirm the
   blast radius" step that should happen before reporting, not after.
5. Ownership: confirm the console's hostname is in scope and belongs to the target
   before reporting a third-party SaaS dashboard that merely shares infrastructure.
