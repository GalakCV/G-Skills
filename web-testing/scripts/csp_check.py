#!/usr/bin/env python3
"""CSP reality check — fetch a URL and report whether inline script would execute.

An XSS payload that reflects is NOT a bug if CSP blocks execution. This reads the
Content-Security-Policy on the actual response so you don't claim XSS on mere reflection.
Read-only: a single GET.

Usage: csp_check.py <url>
"""
import sys
import urllib.request


def main():
    url = sys.argv[1]
    req = urllib.request.Request(url, headers={"User-Agent": "recon-csp-check"})
    try:
        r = urllib.request.urlopen(req, timeout=12)
        headers = {k.lower(): v for k, v in r.headers.items()}
    except Exception as e:
        print(f"[!] fetch failed: {e}")
        return
    csp = headers.get("content-security-policy", "")
    nosniff = headers.get("x-content-type-options", "").lower() == "nosniff"
    print(f"url: {url}")
    print(f"CSP: {csp or '(none)'}")
    print(f"X-Content-Type-Options nosniff: {nosniff}")
    if not csp:
        print("verdict: NO CSP — inline script would execute if reflected. Test it.")
        return
    directive = ""
    for part in csp.split(";"):
        part = part.strip()
        if part.startswith("script-src"):
            directive = part
            break
    if not directive:
        for part in csp.split(";"):
            if part.strip().startswith("default-src"):
                directive = part.strip()
                break
    unsafe_inline = "'unsafe-inline'" in directive
    print(f"effective script directive: {directive or '(default)'}")
    if unsafe_inline:
        print("verdict: 'unsafe-inline' present — inline script CAN run. Reflected XSS likely exploitable.")
    else:
        print("verdict: inline script BLOCKED by CSP. A reflected payload is NOT a working XSS.")
        print("         Surviving vector needs a same-origin 'self' script source (see runbook).")


if __name__ == "__main__":
    main()
