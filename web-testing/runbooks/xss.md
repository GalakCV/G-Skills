# Technique: XSS (reflected / stored / DOM) — with a CSP reality check

Find where input is reflected into a page and executes as script in the app's origin. The
hard part is not reflection — it's execution surviving encoding and CSP.

## Find reflection
Parameters, path segments, headers, and stored fields that appear in a response. Note the
exact **context**: HTML body, attribute, JS string, URL, CSS, or an SVG/HTML attachment.

## Context decides the payload
- HTML body → tag injection; attribute → break out of the attribute; JS string → break the
  string/quote; URL → `javascript:`; DOM sink → trace `source → sink` in the JS.
- First test if the reflection is encoded. If `<`, `"`, `'` come back encoded, the context
  is likely safe — don't claim XSS on mere reflection.

## The CSP reality check (do this before claiming XSS)
A payload that reflects is NOT XSS if CSP blocks execution.
- Read the `Content-Security-Policy` on the actual response. `default-src 'self'` with no
  `'unsafe-inline'` blocks inline `<script>` and inline event handlers.
- A same-origin `<script src>` may still be allowed by `script-src 'self'` — but that needs
  an HTML-injection point AND a same-origin script source; it's not self-contained.
- **Open the browser console.** A `Refused to execute inline script …` message means CSP
  held — that's a mitigation, not a bug. Report the reflection as lower severity, honestly.

## Stored XSS & attachments
- Stored is higher impact (fires for other users). But an SVG/HTML attachment that only
  runs when DOWNLOADED and opened from `file://` is NOT app-origin XSS — it's not
  same-origin, needs manual download, and is generally N/A. Prove execution in the app
  origin (the `http(s)://target/...` URL in the address bar), not from a local file.
- Servers often normalize uploaded MIME types — a type-filter bypass found statically may
  be unreachable. Confirm the stored type and the serving disposition before claiming it.

## Confirm & report
- Evidence: the input + the executed proof IN THE APP ORIGIN (an alert with `document.domain`
  showing the target, console clean of CSP blocks). CWE-79. State reflected vs stored vs DOM,
  and the exact context. If CSP blocked it, say so and downgrade — don't overstate.
