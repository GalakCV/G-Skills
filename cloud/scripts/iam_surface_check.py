#!/usr/bin/env python3
"""SSRF-to-metadata hypothesis flagger — STATIC ANALYSIS ONLY, sends no payload.

Takes the param inventory already produced by recon (host, path, param triples from
katana/gau/arjun) and flags parameters whose name or observed value SHAPE suggests the
app fetches a URL server-side: webhook, callback, url=, uri=, src=, fetch, import,
proxy, render, pdf-from-url, screenshot, avatar-from-url, redirect chains that accept
an absolute URL.

Each hit is a HYPOTHESIS for the (gated) metadata-reach phase to confirm later — this
script never requests 169.254.169.254, metadata.google.internal, or any internal IP.
It only reads the param inventory already on disk.

Usage: iam_surface_check.py <param_inventory.tsv>
param_inventory.tsv columns: host\tpath\tparam  (tab-separated, header optional)
"""
import re
import sys

SSRF_PARAM_PATTERNS = [
    r"url", r"uri", r"link", r"src", r"href", r"path", r"dest", r"redirect",
    r"callback", r"webhook", r"fetch", r"proxy", r"import", r"load",
    r"render", r"screenshot", r"pdf", r"avatar", r"image", r"file",
    r"endpoint", r"target", r"host", r"domain", r"feed", r"rss",
]
SSRF_PATH_PATTERNS = [
    r"export", r"convert", r"render", r"screenshot", r"preview", r"thumbnail",
    r"proxy", r"fetch", r"import", r"webhook", r"notify", r"callback", r"pdf",
]

PARAM_RE = re.compile("|".join(SSRF_PARAM_PATTERNS), re.IGNORECASE)
PATH_RE = re.compile("|".join(SSRF_PATH_PATTERNS), re.IGNORECASE)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    seen = set()
    for line in open(sys.argv[1]):
        line = line.rstrip("\n")
        if not line or line.lower().startswith("host\t"):
            continue
        cols = line.split("\t")
        if len(cols) < 3:
            continue
        host, path, param = cols[0], cols[1], cols[2]
        param_hit = bool(PARAM_RE.search(param))
        path_hit = bool(PATH_RE.search(path))
        if not (param_hit or path_hit):
            continue
        key = (host, path, param)
        if key in seen:
            continue
        seen.add(key)
        reason = "param-name" if param_hit else "path-shape"
        print(f"{host}\tpath={path}\tparam={param}\treason={reason}\t"
              f"hypothesis=possible-server-side-fetch\taction=queue-for-gated-metadata-reach")

    if not seen:
        print("# no SSRF-shaped params found in this inventory", file=sys.stderr)


if __name__ == "__main__":
    main()
