# Runbook: CDN origin-IP leak

1. From recon, identify hosts fronted by a CDN/WAF (Cloudflare, Akamai, Azure Front
   Door, CloudFront, Fastly) via the `cdn` column already in the surface table.
2. Run `scripts/cdn_origin_check.py <host> payloads-or-ranges/<provider>-ip-ranges.txt
   [dns_history.tsv] [tls_san.tsv]`.
   - CDN IP ranges are public (Cloudflare: `https://www.cloudflare.com/ips-v4`, AWS:
     the published `ip-ranges.json` filtered to the CLOUDFRONT service, Fastly:
     `https://api.fastly.com/public-ip-list`). Fetch once, cache in `payloads/`.
   - `dns_history.tsv` / `tls_san.tsv` are whatever you already collected this run —
     this script does not call out to a paid DNS-history API itself.
3. A hit = an IP that answers for the Host header and sits **outside** the CDN's
   published ranges. One HEAD/GET confirms it; that single request is the proof.
4. Why it matters: if the origin is reachable directly, every WAF rule, rate limit, and
   bot-mitigation rule in front of the CDN is moot for that host — but that's a
   separate, larger test (re-running your other active-safe checks against the origin
   IP) and is itself still active-safe as long as it stays read-only and in-scope.
   Report the origin exposure first; only chase "what does the WAF normally block"
   if you have time, since it's a secondary angle on the same root cause.
5. False positives: a second, legitimately public IP for a multi-CDN setup, or a
   dev/staging host that was never put behind the CDN at all (not a leak — just an
   unprotected host, which is still worth noting but under `misconfig`, not here).
