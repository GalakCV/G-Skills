#!/usr/bin/env python3
"""Subdomain takeover detector — dangling CNAME -> claimable-service match.

For each in-scope host: resolve its CNAME. If the CNAME target does not resolve, or the
host returns a known "unclaimed service" fingerprint, flag it. Rank by whether the service
is takeover-prone. DETECTION ONLY — never claims the resource.

Usage: takeover_check.py <hosts.txt> <fingerprints.txt>
fingerprints.txt lines: <service>|<cname-substring>|<http-fingerprint>|<claimable yes/no>
"""
import sys
import socket
import urllib.request


def resolves(host):
    try:
        socket.gethostbyname(host)
        return True
    except Exception:
        return False


def cname_of(host):
    try:
        return socket.gethostbyname_ex(host)[1]
    except Exception:
        return []


def body(host):
    for scheme in ("https", "http"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(f"{scheme}://{host}", headers={"User-Agent": "recon-tko"}), timeout=8)
            return r.read(4096).decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            try:
                return e.read(4096).decode("utf-8", "ignore")
            except Exception:
                return ""
        except Exception:
            continue
    return ""


def main():
    fps = []
    for line in open(sys.argv[2]):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) == 4:
            fps.append(parts)  # service, cname_sub, http_fp, claimable
    for line in open(sys.argv[1]):
        host = line.strip()
        if not host:
            continue
        aliases = cname_of(host)
        alias_blob = " ".join(aliases).lower()
        page = body(host).lower()
        for service, cname_sub, http_fp, claimable in fps:
            hit_cname = cname_sub and cname_sub.lower() in alias_blob
            hit_http = http_fp and http_fp.lower() in page
            if hit_cname or hit_http:
                dangling = bool(aliases) and not any(resolves(a) for a in aliases)
                print(f"{host}\tservice={service}\tclaimable={claimable}\t"
                      f"dangling_cname={dangling}\tmatch={'cname' if hit_cname else 'http'}")
                break


if __name__ == "__main__":
    main()
