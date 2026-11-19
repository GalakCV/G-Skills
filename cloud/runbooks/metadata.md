# Runbook: metadata reachability

Cloud metadata (169.254.169.254 and provider variants) is reachable only through an SSRF.
- If web-testing confirmed an SSRF on an in-scope host, point it at the metadata endpoints
  in payloads/metadata-endpoints.txt and observe whether the service responds.
- Reachability IS the finding. STOP there.
- NEVER retrieve IAM credentials, NEVER use them, NEVER enumerate the account. Fetching and
  using credentials is data theft and account compromise — out of bounds.
- Evidence: the SSRF request + the metadata service responding (a non-credential path like
  the index is enough). Report "metadata reachable via SSRF on <host>".
