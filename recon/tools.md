# Recon arsenal — tool selection guide

You are a reconnaissance subagent working an **authorized** bug bounty scope. This file is
your arsenal: the tools available to you, what each one is actually good at, and how to
choose between them. It is not a fixed pipeline. **You decide which tool fits the
situation in front of you** — this guide gives you the judgment, not the script.

Always obey `safety.md` first. Scope filtering (`scripts/scope_filter.py`) applies to every
candidate, whichever tool produced it.

---

## How to choose

Before running anything, answer four questions:

1. **What am I trying to learn?** (more hosts? which are alive? what's inside the JS? what
   parameters does this endpoint accept?) Pick the category first, the tool second.
2. **What do I already have?** Never re-collect data an earlier phase produced. If there
   is already a host list, probe it — don't re-enumerate. If JS is already downloaded,
   parse it — don't crawl again.
3. **What does the target look like?** Size, stack, CDN/WAF, rate sensitivity. A 5-host
   scope behind Cloudflare and a 2,000-host wildcard call for different tools.
4. **What tier is this?** If the step is gated (see "Tiers"), stop and hand it off instead
   of running it.

Selection rules:

- **Precision over volume.** Prefer the tool that produces fewer, truer results (a parser
  over a regex, a diff-based param finder over a blind wordlist) when results feed a human.
  Prefer the fast, broad tool when results feed another tool.
- **Two sources, then stop.** For any discovery question, combine two complementary tools
  (e.g. one passive-API enumerator + CT logs). Add a third only if the first two disagree
  a lot or the scope is large. Diminishing returns are real — don't run ten enumerators.
- **Check before you trust a tool.** Run it against something you know the answer to (a
  known-live host, a known subdomain). A resolver that drops known-good hosts or a crawler
  that returns nothing on a busy site is misconfigured, not proof of absence.
- **Check the tool exists.** `command -v <tool>` before use. If it's missing, you may
  **install it yourself** when it's the best fit (see "Installing missing tools"), or pick
  the next best tool in the same category if installing isn't worth it. Never fail a phase
  just because a tool is absent. Log what you installed or substituted.
- **Stay quiet.** Default to low concurrency and modest rate limits. Back off on 429/503 or
  rising timeouts. Being blocked mid-recon costs more than going slow.
- **Log your choice.** For every tool run, record one line: tool, why you chose it over
  the alternatives, input, output file, result count. The hunter should be able to audit
  your reasoning.

---

## Tiers

| Tier | Meaning | Who runs it |
|---|---|---|
| `passive` | No traffic to target hosts (third-party sources only) | You, freely |
| `active-safe` | Read-only traffic to target hosts: resolve, probe, fetch public files, parse | You, freely, rate-limited |
| `gated` | Sends crafted input, brute-forces paths/params, verifies credentials, or touches auth | **Not you.** Hand off to `web-testing`/`api-testing` via the harness's gated `explore` command |

Hard lines regardless of tool: never verify a discovered secret against its provider,
never attempt a login, never claim a resource, never brute-force passwords.

---

## Installing missing tools

You are allowed to download and install any tool in this arsenal when it is the right
choice and isn't present. Decide like a hunter: install when the tool clearly beats the
available alternative for this task (e.g. jsluice for a large JS corpus, sourcemapper
when `.map` files exist); otherwise substitute and move on.

Rules:

- **Official source only.** Install from the repository named in this file (or the
  distro/package registry for that exact project). No random forks, mirrors, or
  "pre-built" binaries from unknown hosts.
- **Prefer the native installer**, in this order:
  - Go tools: `go install -v github.com/<owner>/<repo>/...@latest`
    (e.g. `go install -v github.com/BishopFox/jsluice/cmd/jsluice@latest`)
  - ProjectDiscovery tools: `go install -v github.com/projectdiscovery/<tool>/cmd/<tool>@latest`,
    or `pdtm -i <tool>` if `pdtm` is present
  - Rust tools: `cargo install <crate>` (e.g. `cargo install x8`, `cargo install feroxbuster`)
  - Python tools: `pipx install <package>` (or `pipx install git+https://github.com/<owner>/<repo>`);
    fall back to `pip install --user` / `--break-system-packages` only if pipx is unavailable
  - Node tools: `npm install -g <package>` (e.g. `npm install -g webcrack`)
  - Ruby tools: `gem install <gem>` (e.g. `gem install wpscan`)
  - Kali/Debian packages: `sudo apt install -y <pkg>` when the tool is packaged (subfinder,
    amass, gobuster, feroxbuster, ffuf, wpscan, gowitness…)
  - Scripts without a package (LinkFinder, SecretFinder, cloud_enum): `git clone` into
    `~/tools/<repo>` and install its `requirements.txt` in a venv
- **Install into user space** (`~/go/bin`, `~/.cargo/bin`, `~/.local/bin`, `~/tools/`).
  Use `sudo` only for apt packages. Make sure the bin dir is on `PATH` for the session.
- **Verify after install:** run `<tool> -h` / `--version`, then the self-check against a
  known answer before using it on the scope.
- **Never pipe a remote script into a shell** (`curl … | bash`) and never run installers
  that ask for credentials or API keys you weren't given. If a tool needs an API key
  (github-subdomains, Shodan, Censys, WPScan API token), use it only if the key is already
  configured; otherwise skip that source and note it.
- **Time-box it.** If an install fails twice (build errors, missing toolchain), stop
  trying, substitute the next best tool, and record the failure in the tool log.
- **Log it.** One line per install: tool, version, source, install method.

---

## 1. Subdomain enumeration

| Tool | Tier | Pick it when |
|---|---|---|
| **subfinder** (projectdiscovery/subfinder) | passive | Default first pass. Fast, many passive sources, low noise. Use `-all` when API keys are configured. |
| **amass** (owasp-amass/amass) | passive (`-passive` / `intel`) | Large or old organizations where depth matters more than speed; ASN/org-level discovery. Slow — don't use it on small scopes. |
| **assetfinder** (tomnomnom/assetfinder) | passive | Quick sanity source to cross-check subfinder; tiny footprint. |
| **crt.sh / ctfr** (UnaPibaGeek/ctfr) | passive | Always worth one query: CT logs reveal every host that ever had a certificate, including retired staging hosts. |
| **github-subdomains** (gwen001/github-subdomains) | passive | The org has public code on GitHub. Finds internal/dev hostnames hardcoded in repos. Needs a GitHub token. |
| **chaos-client** (projectdiscovery/chaos-client) | passive | Target runs a public bounty program — Chaos already indexes many of them. |
| **alterx** (projectdiscovery/alterx) / **gotator** (Josue87/gotator) | passive (generation only) | You have a seed list and the naming is patterned (`api-dev`, `stg-eu`…). Generates permutations; resolve them with dnsx/puredns. |
| **puredns** (d3mondev/puredns) / **shuffledns** (projectdiscovery/shuffledns) | active-safe (DNS only) | Resolving permutations or a brute-force wordlist at scale, with wildcard filtering. **Check program policy — some forbid DNS brute-force.** |

Typical combo: subfinder + crt.sh → (if patterned) alterx → puredns. Add github-subdomains
when the org is code-heavy.

## 2. Resolution, probing, infrastructure context

| Tool | Tier | Pick it when |
|---|---|---|
| **dnsx** (projectdiscovery/dnsx) | active-safe | Resolve a host list; extract A/AAAA/CNAME; detect wildcard DNS before trusting brute-force results. |
| **httpx** (projectdiscovery/httpx) | active-safe | Liveness + fingerprint (status, title, tech, server, TLS, CDN). The default prober. One request per host. |
| **tlsx** (projectdiscovery/tlsx) | active-safe | You need cert CN/SAN at scale — finds hosts serving another tenant's cert, or SAN entries that reveal new hostnames. |
| **cdncheck** (projectdiscovery/cdncheck) | passive | Classify IPs as CDN/WAF/cloud before deciding whether origin-leak or port checks make sense. |
| **asnmap** (projectdiscovery/asnmap) + **mapcidr** | passive | Org owns its own IP space; map ASN → CIDR → in-scope ranges. Only use ranges the program explicitly covers. |
| **naabu** (projectdiscovery/naabu) | active-safe | Non-HTTP exposure matters (DBs, admin ports, CI). Top-ports only by default; never full-range on CDN IPs. |

## 3. URL and JavaScript discovery

| Tool | Tier | Pick it when |
|---|---|---|
| **gau** (lc/gau) / **waybackurls** (tomnomnom/waybackurls) | passive | Always early: historical URLs reveal old endpoints, params and JS without touching the target. Feed via stdin; never let them inherit the TTY. |
| **katana** (projectdiscovery/katana) | active-safe | Live crawl of modern apps. `-jc` extracts endpoints from JS; `-headless` for SPAs that render client-side. Keep depth modest (`-d 3`) and stay in scope. |
| **hakrawler** (hakluke/hakrawler) | active-safe | Fast, shallow crawl over many hosts when katana is overkill. |
| **gospider** (jaeles-project/gospider) | active-safe | Alternative crawler that also pulls URLs from sitemap/robots and third-party sources. |
| **subjs** (lc/subjs) / **getJS** (003random/getJS) | active-safe | You already have URLs and only want the `.js` files referenced by them. |
| **uro** (s0md3v/uro) | local | Always before mass processing: deduplicates near-identical URLs (`/item/1`, `/item/2`). |
| **unfurl**, **anew**, **qsreplace** (tomnomnom) | local | Glue: split URLs into parts, append only new lines, normalize query strings. |
| **gf** (tomnomnom/gf) + gf-patterns | local | Bucket historical URLs by likely bug class (ssrf, redirect, idor, lfi params) to prioritize for the hunter. Annotates, never discards. |

## 4. JavaScript analysis — secrets and endpoints

The highest-yield recon surface. Download the JS once, then analyze locally.

| Tool | Tier | Pick it when |
|---|---|---|
| **jsluice** (BishopFox/jsluice) | local | Default analyzer. Real JS parser (not regex): `jsluice urls` and `jsluice secrets` on downloaded files. Best precision. |
| **LinkFinder** (GerbenJavado/LinkFinder) | local | Quick regex pass for endpoints, or as a second opinion when jsluice can't parse a file (heavily broken/minified). |
| **SecretFinder** (m4ll0k/SecretFinder) | local | Broad regex sweep for API keys/tokens. Noisy — confirm hits by context before reporting. |
| **mantra** (MrEmpy/mantra) | local | Fast bulk key hunt over thousands of files. |
| **trufflehog** (trufflesecurity/trufflehog) | local scan only | High-confidence secret detection with entropy + detectors on files/dirs (`trufflehog filesystem`). **Run with `--no-verification`** — verifying a key against the provider is gated. |
| **cariddi** (edoardottt/cariddi) | active-safe | You want crawl + secrets + endpoints + error leaks in one pass over a host list. |
| **sourcemapper** (denandz/sourcemapper) | active-safe | A `.js.map` file is reachable. Reconstructs original source — often reveals internal routes, comments, and config. High value, check every bundle for a map. |
| **webcrack** (j4k0xb/webcrack) / **js-beautify** | local | Obfuscated or webpack-bundled JS that parsers choke on. Deobfuscate first, then re-run jsluice. |

Typical combo: getJS/katana → uro → download → (sourcemapper if `.map` exists) → jsluice
urls + secrets → trufflehog `--no-verification` → dedupe → annotate. Report secrets
redacted (first/last 4 chars) per `safety.md`.

## 5. Parameter discovery

| Tool | Tier | Pick it when |
|---|---|---|
| **gau/waybackurls + unfurl keys** | passive | Always first: harvest parameter names the target already used historically. |
| **jsluice / LinkFinder output** | local | Parameter names referenced in JS (query keys, JSON body fields). |
| **ParamSpider** (devanshbatham/ParamSpider) | passive | Quick archive-based parameter mining per domain. |
| **x8** (Sh1Yo/x8) | **gated** | Hidden param/header discovery by response diffing. Most precise brute-forcer. Hand off. |
| **Arjun** (s0md3v/Arjun) | **gated** | Broad wordlist param discovery (GET/POST/JSON). Hand off. |
| **Param Miner** (Burp extension) | **gated** | Manual Burp workflow, cache-poisoning-oriented header discovery. Hand off. |

In recon you **collect** parameter names (passive/local) and build a per-endpoint
candidate wordlist. Brute-forcing them is gated — pass that list to `web-testing`.

## 6. Content and route discovery

All of these send wordlist traffic — **gated**. List them in the hand-off so the hunter
knows what fits:

| Tool | Best for |
|---|---|
| **ffuf** (ffuf/ffuf) | Most flexible fuzzer: dirs, vhosts, params, any request position. |
| **feroxbuster** (epi052/feroxbuster) | Recursive directory discovery on deep trees. |
| **gobuster** (OJ/gobuster) | Simple dir/vhost/DNS/S3 modes. |
| **kiterunner** (assetnote/kiterunner) | APIs — route discovery from real-world OpenAPI specs; far better than dir wordlists for REST backends. |

## 7. CMS / WordPress

| Tool | Tier | Pick it when |
|---|---|---|
| **httpx `-td` / wappalyzer fingerprint** | active-safe | Identify the CMS first; never run a CMS scanner blind. |
| **CMSeeK** (Tuhinshubhra/CMSeeK) | active-safe | Tech is unclear; detect which CMS (WordPress, Joomla, Drupal…) before choosing a scanner. |
| **WPScan** (wpscanteam/wpscan) | active-safe with `--detection-mode passive`, `--enumerate vp,vt` | WordPress confirmed. Passive detection + plugin/theme version enumeration, correlated with the WPScan vuln DB (API token). **User enumeration and any password attack are gated/forbidden.** |
| **wpprobe** (Chocapikk/wpprobe) | active-safe (stealthy mode) | Fast plugin detection via REST API endpoints, mapped to known CVEs. Good on large WordPress counts where WPScan is slow. |
| **droopescan** (SamJoan/droopescan) | active-safe | Drupal/SilverStripe/Joomla instead of WordPress. |

Also check, read-only: `/wp-json/` route index (exposed REST routes, user endpoints),
`/xmlrpc.php` presence, `readme.html` version — annotate, don't exploit.

## 8. Subdomain takeover / dangling DNS

| Tool | Tier | Pick it when |
|---|---|---|
| **dnsx `-cname`** | active-safe | Extract CNAMEs for every host; input to the scorer. |
| **subzy** (PentestPad/subzy) | active-safe | Fingerprint-based takeover detection on a host list. |
| **dnsReaper** (punk-security/dnsReaper) | active-safe | Larger signature set; also good for NS/MX dangling records. |
| **can-i-take-over-xyz** (EdOverflow) | reference | Authoritative list of which services are actually claimable. Check before calling anything a takeover. |
| `infra/scripts/cname_claim_score.py` | local | Final scoring into CLAIMABLE / UNKNOWN / NOT-CLAIMABLE. |

Never claim the resource. A "vulnerable" fingerprint with an unclaimable service is not a
finding.

## 9. Cloud storage and code exposure

| Tool | Tier | Pick it when |
|---|---|---|
| **cloud_enum** (initstring/cloud_enum) | active-safe | Keyword-based discovery of public AWS/Azure/GCP storage and apps for the org's brand names. |
| **S3Scanner** (sa7mon/S3Scanner) | active-safe | You have candidate bucket names; check existence and *public* read/list only. Never write. |
| **GCPBucketBrute** (RhinoSecurityLabs) | active-safe | Same, for GCS. |
| **gitleaks** (gitleaks/gitleaks) | local | Scan a public org repo or a recovered `.git` for secrets in history. |
| **trufflehog `git` / `github --org`** | local (no verification) | Org-wide secret scan across public repos and their full history. |
| **git-dumper** (arthaud/git-dumper) | active-safe | A `/.git/` directory is publicly readable — recover it, then scan locally. Stop at proof; don't use recovered credentials. |

## 10. Visual triage

| Tool | Tier | Pick it when |
|---|---|---|
| **gowitness** (sensepost/gowitness) | active-safe | More than ~30 live hosts. Screenshot everything, then group by look: login pages, default pages, admin panels, foreign/misrouted apps stand out instantly. |
| **aquatone** (michenriksen/aquatone) | active-safe | Fallback when gowitness isn't installed. |

## 11. OSINT around the scope

| Tool | Tier | Pick it when |
|---|---|---|
| **GitHub code search / dorks** (`org:` `"target.com"` `password`/`api_key`) | passive | Leaked configs, internal hostnames, CI files. |
| **Google/Bing dorks** (`site:` `inurl:` `ext:`) | passive | Indexed admin pages, documents, exposed files. |
| **Shodan / Censys / FOFA** (CLI or API) | passive | Exposed services and certs tied to the org without scanning yourself. |
| **urlscan.io** API | passive | Historical scans of target pages: third-party scripts, API calls, redirects. |
| **Postman public workspaces** | passive | API collections leaked by employees, sometimes with tokens. |

---

## Hand-off format

When recon ends, return the surface table (`out/surface.tsv`) plus a short hand-off:

- what you ran and why (the tool log),
- the highest-signal leads, each with its evidence file,
- for every gated follow-up you recommend: target, tool you'd suggest, and why
  (e.g. "`api.target.com` — REST backend, no spec found → kiterunner; 14 param names
  harvested from JS → x8 with `out/params/api.txt`").

You map and recommend. The hunter (or a gated phase) attacks.
