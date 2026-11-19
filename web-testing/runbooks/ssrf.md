# Technique: SSRF (server-side request forgery)

Find where the server fetches a URL you control, then prove it makes a request on your
behalf — safely, without pivoting into internal systems beyond minimal proof.

## Find the sinks
Any feature where the server fetches a URL: webhooks, URL preview, avatar/image-from-URL,
import-from-URL, PDF/screenshot generators, link unfurlers, open-redirect-fed fetchers,
XML/SVG external entities.

## Confirm (use your own collaborator)
- Point the fetch at a host YOU control (a request catcher / collaborator domain). An
  inbound hit proves the server made the request — that alone is the SSRF confirmation.
- Observe whether it's full-response (you see the fetched body) or blind (only the callback
  fires). Both are reportable; note which.

## Scope of proof — do NOT over-reach
- Confirming the callback is enough. Do NOT then scan the internal network, pull cloud
  metadata credentials, or access internal services beyond a single proof that an internal
  address is reachable (e.g. a different response for an internal vs external host).
- Cloud metadata (`169.254.169.254`) is a high-impact proof point, but STOP at showing it's
  reachable — do not retrieve and use real credentials. Reachability + the endpoint
  responding is the evidence.

## Bypasses to test (safely)
- Alternate IP encodings, redirects to internal, DNS rebinding, `[::]`/`0.0.0.0`,
  allowlist gaps (`@`, `#`, subdomain tricks). Test to defeat a filter, not to breach.

## Confirm & report
- Evidence: the input URL + the collaborator hit (timestamp, source IP) or the internal-vs-
  external response difference. CWE-918. State blind vs full-response and the reachability
  you proved — without having exfiltrated internal data.
