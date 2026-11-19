# Technique: file upload

Find where the app accepts a file, then test whether you can store content the server will
later serve or execute in a dangerous way. Confirm the full chain, not just the upload.

## Map the upload + the serving
- Where files are accepted (attachments, avatars, imports) and HOW they're served back
  (download link, inline preview, direct path). The bug is in the SERVING, not just the
  accepting — always trace both halves.
- Note: client-declared `Content-Type`, extension handling, and whether the server
  re-derives/normalizes the type (it often does — a client-set MIME may not survive).

## What to test
- **Type/extension bypass**: does a dangerous type pass the filter via a parameter
  (`image/svg+xml;charset=utf-8`), double extension, case, or null byte? VERIFY what gets
  stored — query the stored type if you can; the server may normalize it away.
- **Served inline vs download**: does the server serve your file with `Content-Disposition:
  inline` and a renderable type? An attachment forced to download has no app-origin impact.
- **Server-side execution**: in stacks that execute uploads (PHP/JSP in a web-served dir),
  does an uploaded script run when requested? High impact — but confirm it's reachable and
  served, not just stored.
- **Path traversal in filename**: `../` in the stored name writing outside the upload dir.
- **SVG/HTML → XSS**: only counts if served inline in the app origin with script execution
  (see xss.md and the CSP check) — a download that runs from `file://` is N/A.

## The full-chain discipline (don't stop at "it uploaded")
Upload accepted → stored type/name → served how → executes/renders where. A finding needs
the whole chain observed. A type bypass that the server normalizes on store, or a file
forced to download, is not exploitable — say so honestly.

## Confirm & report
- Evidence: the upload request, the STORED type/name (if observable), and the serving
  response (headers + disposition) or execution proof in the app origin. CWE-434/CWE-79/
  CWE-22. State exactly which half of the chain holds and which mitigation (if any) stops it.
