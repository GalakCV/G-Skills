# Technique: JavaScript recon

Goal: pull the client-side JS of live hosts and surface hidden endpoints, parameters,
and access-control hints — as HYPOTHESES, verified by a real probe before they count.

## Collect

- Crawl + collect JS with `katana -silent -jc` (feed seed URLs on stdin). Add any `.js`
  found via wayback/gau historically.
- Fetch each in-scope `.js` (respect scope + rate limit). Do not fetch out-of-scope.

## Extract (deterministic first), then judge

1. Deterministically grep candidates from each JS: paths/routes, parameter names,
   and secret-like strings (but NEVER output a secret value — redact it; see safety.md).
   This raw list includes framework noise (Next.js `/_next/static/chunks/*`, MIME types
   like `image/png`, library URLs, namespaces) — it is UNFILTERED material.
2. YOU are the filter. From the raw candidates, judge what is a real application route
   or parameter vs noise. Discard framework/static noise.
3. For the real ones, emit a hypothesis with: value, why it's interesting, and how to
   verify (e.g. "GET /api/v2/users/{id} with a low id", "test role= injection on login").

## Verify before claiming

- The harness/agent probes the routes you flag. Interpret the result:
  - 404 → not here (maybe the API lives on another host — note that, don't confirm).
  - 200 on a `.js`/static asset → it's a file, not surface. Drop.
  - 2xx app route / 401 / 403 → confirmed surface. Promote to the inventory.
- Only probe-confirmed routes become confirmed endpoints. The rest stay as hypotheses.

## Notes

- A role model in the JS (admin/user/guest, parent/teacher/student) is a strong
  authz/IDOR lead — record it as a hypothesis with concrete tests, for the human.
