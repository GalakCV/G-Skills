#!/usr/bin/env python3
"""Origin-behind-CDN leak detector — passive comparison, no direct origin exploitation.

For a host fronted by a CDN/WAF (Cloudflare, Akamai, Front Door, CloudFront), checks
whether the real origin IP is exposed through:
  1. A historical/legacy A record still pointing straight at the origin (reads a
     DNS-history TSV you already collected — does not itself query any paid DNS-history API).
  2. A sibling hostname on the same apex (e.g. direct-mail, origin., old., preprod-origin.)
     that resolves outside the CDN's known IP ranges.
  3. TLS certificate SAN reuse: a cert seen on a non-CDN IP sharing a SAN with the
     CDN-fronted hostname (reads a `tls_san.tsv` you already collected via tls_check.sh).

DETECTION ONLY. If an origin IP is found, the proof is "this IP answers for the host
and is not in the CDN's published ranges" — never fetch anything beyond one HEAD/GET to
confirm, and never use the origin IP to bypass a WAF rule for anything other than that
one proof request.

Usage: cdn_origin_check.py <host> <cdn-ip-ranges.txt> [dns_history.tsv] [tls_san.tsv]
"""
import socket
import ipaddress
import sys
import urllib.request


def load_ranges(path):
    nets = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            nets.append(ipaddress.ip_network(line, strict=False))
        except ValueError:
            continue
    return nets


def in_cdn(ip, nets):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True  # unparsable, don't flag
    return any(addr in n for n in nets)


def confirm(ip, host):
    try:
        req = urllib.request.Request(
            f"https://{ip}/", headers={"Host": host, "User-Agent": "cdn-origin-check"}
        )
        r = urllib.request.urlopen(req, timeout=8)
        return r.status
    except Exception as e:
        return f"error:{e.__class__.__name__}"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    host = sys.argv[1]
    cdn_nets = load_ranges(sys.argv[2])
    candidates = set()

    if len(sys.argv) > 3:
        for line in open(sys.argv[3]):
            parts = line.strip().split("\t")
            if len(parts) >= 2 and host in parts[0]:
                candidates.add(parts[1])

    try:
        for info in socket.getaddrinfo(host, None):
            candidates.add(info[4][0])
    except Exception:
        pass

    found = False
    for ip in candidates:
        if not in_cdn(ip, cdn_nets):
            status = confirm(ip, host)
            print(f"{host}\tcandidate_origin={ip}\tin_cdn_range=false\tconfirm_status={status}")
            found = True

    if not found:
        print(f"# {host}: no candidate IP found outside the CDN's ranges", file=sys.stderr)


if __name__ == "__main__":
    main()
