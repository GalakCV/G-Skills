# Technique: auth enforcement (missing / broken authentication)

The highest-yield API bug. The front-end gates you at an SSO login, but the API endpoints
behind it may not actually enforce the token. Test the API directly.

## The core test: no-token request
- Take endpoints the spec declares as Bearer-protected (or any data endpoint found in JS).
- Send a plain GET with **no `Authorization` header**, no cookie.
- Read the result:
  - **401/403** → auth enforced (expected). Good — move on.
  - **200 with real data** → broken/missing authentication. High impact, especially if the
    data was meant to be internal/employee-only. STOP on that endpoint, capture ONE minimal
    redacted record as proof, do not pull more.
  - **404/405** → route not deployed here / wrong method.

## Pick safe endpoints first
From the spec, choose GETs with no required params that sound read-only and low-sensitivity
(health, config, list/metadata, lookups). Avoid anything that returns bulk PII until you've
confirmed the enforcement gap on a benign endpoint.

## Other auth weaknesses to test
- **Token not validated**: a malformed/expired/other-user's-shaped token still accepted
  (test with a clearly invalid token you own — never a real user's).
- **Alg/signature issues**: `alg:none`, unsigned JWT accepted (confirm the server accepts
  it; do not forge a real identity to access real data).
- **Session fixation / missing expiry**: a token that never expires or is reusable.
- **Verb-based bypass**: GET blocked but HEAD/OPTIONS or a different method leaks.

## Confirm & report
- Evidence: the request WITHOUT auth + the response returning protected data (minimal,
  redacted). State the expected auth model (from the spec/security scheme) vs observed.
  CWE-287/CWE-306. If everything returns 401, auth works — report the exposed spec as info
  only, honestly.
