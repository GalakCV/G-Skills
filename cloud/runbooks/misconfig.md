# Runbook: cloud misconfiguration

Detection + reachability only. Look for, tied to the in-scope target:
- Public EBS/RDS snapshots, public AMIs (provider consoles / APIs the program allows).
- Open storage browsers / directory indexes on cloud-hosted static sites.
- Exposed cloud management dashboards, Kubernetes dashboards, container registries.
Prove it's reachable/public and owned by the target; capture minimal evidence; never log in
with found credentials, never change configuration.
