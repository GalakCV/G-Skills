# Runbook: subdomain takeover

1. `scripts/takeover_check.py <hosts.txt> payloads/takeover-fingerprints.txt`.
2. For each hit, read the columns: service, claimable, dangling_cname, match.
   - `claimable=yes` + a dangling/unclaimed fingerprint -> real takeover candidate.
   - `claimable=no` (e.g. deleted CloudFront) -> weak signal; usually NOT trivially
     claimable. Note it, don't over-claim.
3. Rank: S3 / GitHub Pages / Heroku / Azure / Fastly / Shopify = high. CloudFront = low.
4. PROOF ONLY — do NOT register/claim the resource. Report the in-scope host, its dangling
   CNAME target, and the matched claimable service. Claiming it can disrupt the target and
   exceeds a responsible proof; most programs accept the detection as the finding.
