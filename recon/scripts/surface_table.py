#!/usr/bin/env python3
"""Build the complete annotated surface inventory from httpx output.

Coverage, not pruning: one row per host, signals ANNOTATE (never drop a host).
Status is reported exactly as observed. Writes a TSV the hunter reads.

Usage: surface_table.py <run_dir>
"""
import sys
import json
import os
import re

ADMIN = re.compile(r"\b(admin|console|dashboard|portal|backoffice)\b", re.I)
AUTH = re.compile(r"\b(login|sign\s?in|sso|oauth|auth|account)\b", re.I)
API = re.compile(r"\b(api|graphql|swagger|openapi|rest|v\d)\b", re.I)
DEV = re.compile(r"\b(dev|stag|staging|uat|qa|test|sandbox|preprod|internal)\b", re.I)


def signals(rec, host):
    s = []
    blob = f"{host} {rec.get('title','')} {' '.join(rec.get('tech',[]) or [])}"
    if DEV.search(host):
        s.append("dev/staging")
    if API.search(blob):
        s.append("api")
    if AUTH.search(blob):
        s.append("auth")
    if ADMIN.search(blob):
        s.append("admin")
    sc = rec.get("status_code")
    if sc in (401, 403):
        s.append("gated")
    return ";".join(s)


def main():
    run = sys.argv[1]
    jsonl = os.path.join(run, "out", "httpx.jsonl")
    dead = os.path.join(run, "out", "dead.txt")
    out = os.path.join(run, "out", "surface.tsv")
    rows = []
    for line in open(jsonl):
        if not line.strip():
            continue
        r = json.loads(line)
        host = r.get("input", "")
        rows.append([
            host,
            str(r.get("status_code", "")),            # as observed
            ";".join(r.get("tech", []) or []),
            r.get("webserver", ""),
            r.get("cdn_name", ""),
            r.get("location", ""),
            signals(r, host),
            "confirmed",                              # a tool observed it this run
        ])
    if os.path.exists(dead):
        for h in open(dead):
            h = h.strip()
            if h:
                rows.append([h, "dead", "", "", "", "", "", "confirmed"])
    rows.sort(key=lambda x: x[0])
    with open(out, "w") as f:
        f.write("host\tstatus\ttech\tserver\tcdn\tlocation\tsignals\tstate\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"[+] surface table: {len(rows)} rows -> {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
