#!/usr/bin/env python3
"""Scope filter — reads hosts on stdin, writes in-scope hosts on stdout.

Hard rule: out-of-scope always wins. Normalize (lowercase, strip scheme/port/path)
BEFORE matching, so a host that differs only in case is never wrongly dropped.

Usage:
    cat candidates.txt | scope_filter.py scope.json
scope.json: {"seeds": [...], "in_scope": ["*.example.com"], "out_of_scope": [...]}
"""
import sys
import json
import re


def normalize(host: str) -> str:
    host = host.strip().lower()
    host = re.sub(r"^[a-z]+://", "", host)      # strip scheme
    host = host.split("/")[0].split("?")[0]      # strip path/query
    host = host.split(":")[0]                     # strip port
    host = host.rstrip(".")                       # strip trailing dot
    if host.startswith("*."):                     # CT logs emit wildcards
        host = host[2:]
    return host


def match(host: str, pattern: str) -> bool:
    pattern = pattern.strip().lower()
    if pattern.startswith("*."):
        base = pattern[2:]
        return host == base or host.endswith("." + base)
    return host == pattern


def is_valid(host: str) -> bool:
    return bool(re.fullmatch(r"(?=.{1,253}$)([a-z0-9_-]{1,63}\.)+[a-z]{2,}", host))


def main():
    with open(sys.argv[1]) as f:
        scope = json.load(f)
    in_scope = scope.get("in_scope", [])
    out_scope = scope.get("out_of_scope", [])
    seen = set()
    for line in sys.stdin:
        host = normalize(line)
        if not host or host in seen or not is_valid(host):
            continue
        seen.add(host)
        if any(match(host, p) for p in out_scope):   # out-of-scope wins
            continue
        if any(match(host, p) for p in in_scope):
            print(host)


if __name__ == "__main__":
    main()
