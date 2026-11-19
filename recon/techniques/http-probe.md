# Technique: live probe + fingerprint

Goal: confirm which hosts are actually live and characterize each one. Only live hosts
move forward — but "live" includes gated (401/403); those are kept and flagged, not
dropped.

## Tool

- `httpx` (ProjectDiscovery CLI) with JSON output: status code, title, tech, CDN/WAF,
  redirect chain. Feed the host list on stdin.
  Example: `httpx -silent -json -title -tech-detect -status-code -follow-redirects`
- Respect the rate limit (`-rl <n>` or run gently). Stay under the program's cap.

## Read the results honestly

- **2xx** → live app/API/page. Keep, characterize (what is it?).
- **401 / 403** → EXISTS but gated (auth/WAF/edge). Keep and flag as gated — often the
  interesting stuff, but do not call it "attack first" blindly.
- **301 / 302** → note where it redirects (login/SSO = auth boundary; marketing = low).
  If it redirects out of scope, drop that host (see safety.md).
- **404 at root** → host answers but root is empty. Keep it listed as 404; an API can
  404 at `/` while having live paths — note it, don't rank it as a live target.
- **DNS fail / connection refused / timeout** → dead. Record as dead; don't carry it.

## Fingerprint signals to record (not to filter by)

Distinct application, API surface, admin/auth boundary, upload/import, unusual or old
tech stack, an app inconsistent with the parent brand (possible takeover — flag it).
These annotate the inventory; they never remove a host that lacks them.

## Output of this phase

For every probed host: final URL, status, title, tech, and its signals. This feeds the
surface-mapping inventory.
