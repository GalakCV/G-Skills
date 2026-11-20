# Runbook: SSRF-to-metadata surface mapping (hypothesis only)

This phase never touches an internal IP. It reads the param inventory already built by
recon (`out/param_inventory.tsv`) and flags parameters shaped like a server-side URL
fetch (`url=`, `callback=`, `/export`, `/render`, `/screenshot`, `/pdf`, etc.).

1. Run `scripts/iam_surface_check.py out/param_inventory.tsv`.
2. Each hit is a **hypothesis**, not a finding. Rank by how directly the param controls
   a URL the server will fetch (an explicit `url=https://...` beats a vague `src=`).
3. If you have a go-ahead to test one (explore tier, human-gated — see `metadata.md`):
   the actual metadata-reach test sends a single crafted value pointing at the cloud
   provider's metadata IP/hostname (`169.254.169.254`, `metadata.google.internal`,
   `100.100.100.200` for Alibaba) and checks **only whether a response came back that
   looks like metadata** (e.g. an IMDS JSON shape, an Azure `Metadata: true` header
   requirement bypass). **Never read, store, or act on any credential the metadata
   service returns** — reachability is the whole finding.
4. If the param instead returns the literal fetched content (SSRF with response
   reflected), that's a stronger, separately reportable bug on its own — still stop at
   reachability proof, don't pivot into using it to reach other internal hosts without
   a fresh explicit go-ahead for that specific pivot.
