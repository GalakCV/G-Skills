#!/usr/bin/env python3
"""Exposed cloud-native admin console / dashboard detector — fingerprint only.

Checks a list of in-scope hosts for known cloud-native management surfaces left
reachable without auth: Kubernetes dashboard, Azure Function Apps "advanced tools"
(Kudu/SCM), exposed API Management developer portal, GCP/AWS console lookalikes
left on an internal CNAME, Kibana/Grafana/Consul UIs on a cloud-labelled host.

DETECTION ONLY. Never attempts login, never tries default credentials, never
submits a form. A 200/301 on a known path + a known page fingerprint is the
finding; anything else is noise.

Usage: admin_console_check.py <hosts.txt> <fingerprints.txt> [--rate N]
fingerprints.txt lines: <name>|<path>|<body-fingerprint>|<severity note>
"""
import sys
import time
import urllib.request
import urllib.error


def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "cloud-admin-console-check"})
        r = urllib.request.urlopen(req, timeout=timeout)
        return r.status, r.read(8192).decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(8192).decode("utf-8", "ignore")
        except Exception:
            return e.code, ""
    except Exception:
        return None, ""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    rate = 0.3
    if "--rate" in sys.argv:
        rate = 1.0 / float(sys.argv[sys.argv.index("--rate") + 1])

    fps = []
    for line in open(sys.argv[2]):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) == 4:
            fps.append(parts)

    hosts = [h.strip() for h in open(sys.argv[1]) if h.strip()]
    for host in hosts:
        for name, path, fp, note in fps:
            for scheme in ("https", "http"):
                url = f"{scheme}://{host.rstrip('/')}{path}"
                status, body = fetch(url)
                time.sleep(rate)
                if status is None:
                    continue
                if status in (200, 301, 302) and (not fp or fp.lower() in body.lower()):
                    print(f"{host}\tconsole={name}\tpath={path}\tstatus={status}\tnote={note}")
                    break  # don't double-report http+https for the same console


if __name__ == "__main__":
    main()
