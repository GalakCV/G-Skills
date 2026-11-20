# Runbook: CNAME claim-likelihood scoring

Field lesson: a single large recon run can surface 100+ dangling CNAMEs, and the vast
majority are dead CloudFront distributions (deleted, not claimable — re-pointing a
CloudFront alias requires the distribution to exist in *your own* AWS account, which
you don't control). Reporting those, or spending time manually triaging each one, is
how the real 2-3 candidates get lost or delayed.

1. Run `takeover.py` first to get its raw tab-separated output.
2. Run `scripts/cname_claim_score.py <takeover_output.tsv> payloads/takeover-fingerprints.txt`.
3. Work the buckets in this order:
   - **CLAIMABLE** — service is on the known-claimable list and the alias is actually
     dangling. These are your candidates. For each: confirm manually (one more GET to
     the host, read the exact error page) before reporting — fingerprints can be stale.
   - **UNKNOWN** — matched a CNAME substring but didn't confirm via HTTP fingerprint,
     or the service isn't in either list yet. Worth a 2-minute manual look; if it's a
     real service you haven't seen before, add it to `takeover-fingerprints.txt` with
     the correct `claimable` column so future runs classify it automatically.
   - **NOT-CLAIMABLE** — note and move on. Still useful as inventory (dangling DNS is
     technically a finding in some programs' eyes — check program scope), but don't
     spend testing time here.
4. This phase makes no new network requests — it's pure classification of
   `takeover.py`'s output, so it's always active-safe and can run every time without
   re-asking.
