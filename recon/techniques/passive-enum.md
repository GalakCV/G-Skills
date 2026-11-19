# Technique: passive enumeration

Goal: find subdomains of the in-scope seeds from passive sources (no direct traffic to
the target beyond the tools' own lookups). Cheap, quiet, do this first.

## Tools (run via shell)

- `subfinder -d <seed> -silent -all` — passive subdomain sources.
- `assetfinder --subs-only <seed>` — extra passive source.
- `echo <seed> | waybackurls` and `echo <seed> | gau --subs` — historical URLs from
  Wayback/OTX/CommonCrawl; extract hostnames from the URLs (they often reveal hosts
  and endpoints no live crawl shows).

Run per seed. Pipe the domain via stdin for waybackurls/gau (they read stdin), and give
every long-running tool a timeout so one slow source doesn't stall the phase.

## Process

1. For each seed, collect hosts from all tools above.
2. Deduplicate.
3. Extract hostnames from the historical URLs too.
4. Filter EVERY candidate against scope (see safety.md) — keep only in-scope.
5. Pass the surviving host list to the next phase (active-discovery, then probe).

## Notes

- If a tool isn't installed, say so and continue with the others — never block the
  phase on one missing binary.
- Passive results are candidates, not confirmed live — the probe phase decides that.
- Keep the full list; do not drop a host because its name looks boring.
