# Runbook: DNS

- Zone transfer (only if the program permits): `dig AXFR <zone> @<ns>`. A successful
  transfer dumps the zone = misconfig finding.
- Dangling/stale records: records pointing at decommissioned infra (overlaps takeover).
- Detection only; never modify records. Report what was observed.
