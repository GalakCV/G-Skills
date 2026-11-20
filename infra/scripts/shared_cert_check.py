#!/usr/bin/env python3
"""Shared/mismatched TLS certificate detector — tenant & host confusion.

Fetches the live certificate presented by each in-scope host and flags it when:
  (a) the cert's CN/SAN list includes a domain that is NOT the target apex and NOT a
      known CDN/shared-hosting wildcard (i.e. looks like someone else's tenant), or
  (b) the cert's CN/SAN doesn't cover the hostname you connected to at all (classic
      mismatch — may indicate a leftover/forgotten origin or a misrouted LB rule).

This is exactly the class of bug found in the field: a dev/staging host answering
with a certificate issued for a completely unrelated third-party domain, which is a
strong signal of shared infrastructure / tenant bleed-through (e.g. a load balancer or
reverse proxy serving the wrong backend for that SNI).

DETECTION ONLY — one TLS handshake per host, no HTTP request beyond what's needed to
read the cert. Never treat the unrelated domain itself as in-scope; it is reported as
"this host's cert names an unrelated domain", not tested further.

Usage: shared_cert_check.py <hosts.txt> <target-apexes.txt> [known-shared-wildcards.txt]
target-apexes.txt: one apex per line (e.g. fairlife.com)
known-shared-wildcards.txt: optional allowlist of expected shared-CDN SAN patterns
(e.g. *.cloudfront.net, *.azureedge.net) to avoid false positives on normal CDN certs.
"""
import ssl
import socket
import sys


def get_cert_names(host, port=443, timeout=8):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
    names = set()
    for sub in cert.get("subject", ()):
        for key, val in sub:
            if key == "commonName":
                names.add(val)
    for typ, val in cert.get("subjectAltName", ()):
        if typ == "DNS":
            names.add(val)
    return names


def apex_of(name):
    parts = name.lstrip("*.").split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else name


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    hosts = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    target_apexes = {l.strip().lower() for l in open(sys.argv[2]) if l.strip()}
    allow_wild = set()
    if len(sys.argv) > 3:
        allow_wild = {l.strip().lower() for l in open(sys.argv[3]) if l.strip()}

    for host in hosts:
        try:
            names = get_cert_names(host)
        except Exception as e:
            print(f"# {host}: handshake failed ({e.__class__.__name__})", file=sys.stderr)
            continue

        covers_host = any(
            name.lower() == host.lower()
            or (name.startswith("*.") and host.lower().endswith(name[1:].lower()))
            for name in names
        )
        foreign = [
            n for n in names
            if apex_of(n.lower()) not in target_apexes
            and not any(n.lower().endswith(w.lstrip("*.")) for w in allow_wild)
        ]

        if not covers_host:
            print(f"{host}\tissue=cert-does-not-cover-host\tnames={','.join(sorted(names))}")
        if foreign:
            print(f"{host}\tissue=cert-names-unrelated-domain\tforeign={','.join(sorted(foreign))}\t"
                  f"note=HIGH if the foreign domain is clearly a different company/tenant")


if __name__ == "__main__":
    main()
