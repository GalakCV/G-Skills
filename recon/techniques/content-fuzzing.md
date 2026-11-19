# Technique: content fuzzing (ACTIVE — needs human approval)

Goal: discover routes not present in the JS, by fuzzing with the RIGHT wordlist for the
stack — never a blind generic list. This is active and noisy.

## Gate first

Fuzzing is intrusive and many programs restrict automated scanning. Do NOT run it
without the human's explicit go-ahead and confirmation the program allows it. Respect
the rate limit strictly (see safety.md).

## Plan by technology, not by reflex

Choose the wordlist and target from the host's fingerprint and known routes:

- **Next.js / React / Vue SPA** (web root 200s everywhere): directory brute is
  low-value. Aim at the **API** (`api/api-endpoints.txt`, `api/objects.txt`,
  `graphql.txt`) under the known API base, and at **sensitive files**
  (`quickhits.txt`: `.env`, `.git`, source maps).
- **PHP/Apache**: directory+file brute with `php,bak,old` extensions (`raft-*`).
- **ASP.NET/IIS**: `IIS.fuzz.txt`, `aspx,asmx,config`.
- **Java/servlets**: `JavaServlets-Common`, `jsp,do,action`.
- **Known CMS** (WordPress/Drupal): the CMS-specific list.
- Always worth it: `quickhits.txt` for exposed files.

## Execute

- `ffuf -u https://<host><base>/FUZZ -w <chosen wordlist> -mc 200,204,301,302,401,403,405 -ac -rate <limit>`
- `-ac` auto-calibrates soft-404s. Add `-e <ext>` by tech. Cap requests.

## Interpret

Same-length/same-words clusters are a catch-all page, not real content — drop them.
A 403/401 is a real gated path (keep). Confirm real hits into the inventory; discard
noise. Never report a soft-404 as a finding.
