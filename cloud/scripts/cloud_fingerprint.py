#!/usr/bin/env python3
"""Fingerprint the cloud provider for each host, from CNAME and response headers.

Read-only. Helps decide which bucket/asset checks apply. Input: a file of hosts (one per
line, from recon). Output: host -> provider.

Usage: cloud_fingerprint.py <hosts.txt>
"""
import sys
import socket
import urllib.request

SIGS = {
    "aws": ["amazonaws.com", "cloudfront.net", "elb.amazonaws", "s3.", "awsglobalaccelerator"],
    "gcp": ["storage.googleapis.com", "appspot.com", "googleusercontent", "run.app", "cloudfunctions"],
    "azure": ["blob.core.windows.net", "azurewebsites.net", "cloudapp.azure", "azureedge", "trafficmanager.net"],
}


def cname_chain(host):
    try:
        return socket.getaddrinfo(host, None)[0][4][0], socket.gethostbyname_ex(host)[1]
    except Exception:
        return None, []


def server_header(host):
    for scheme in ("https", "http"):
        try:
            r = urllib.request.urlopen(urllib.request.Request(f"{scheme}://{host}", headers={"User-Agent": "recon-fp"}), timeout=8)
            return r.headers.get("Server", "") + " " + r.headers.get("x-amz-request-id", "") + r.headers.get("x-goog-generation", "") + r.headers.get("x-ms-request-id", "")
        except Exception:
            continue
    return ""


def classify(host, aliases, hdr):
    hay = " ".join([host] + list(aliases) + [hdr]).lower()
    for prov, sigs in SIGS.items():
        if any(s in hay for s in sigs):
            return prov
    if "x-amz" in hdr.lower():
        return "aws"
    if "x-goog" in hdr.lower():
        return "gcp"
    if "x-ms-" in hdr.lower():
        return "azure"
    return "unknown"


def main():
    for line in open(sys.argv[1]):
        host = line.strip()
        if not host:
            continue
        _, aliases = cname_chain(host)
        hdr = server_header(host)
        print(f"{host}\t{classify(host, aliases, hdr)}")


if __name__ == "__main__":
    main()
