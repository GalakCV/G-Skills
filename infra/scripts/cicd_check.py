#!/usr/bin/env python3
"""Exposed CI/CD & artifact-repository detector — reachability fingerprint only.

Checks in-scope hosts for Jenkins, GitLab Runner/CI, Artifactory, Nexus, TeamCity,
Bamboo, CircleCI self-hosted, Drone, and Argo CD left reachable without auth. These
surfaces are high-value because they often leak build logs, environment variables,
internal hostnames, and sometimes unauthenticated API endpoints that list jobs/builds.

DETECTION ONLY:
  - Never log in, never try default credentials (admin/admin, admin/<empty>).
  - Never trigger a build, never read a specific job's console output beyond what's
    needed to confirm the product (a job LIST is evidence enough; don't open build logs).
  - Never download an artifact from Artifactory/Nexus even if listing is public —
    note that artifacts are downloadable, don't download one.

Usage: cicd_check.py <hosts.txt> <fingerprints.txt>
fingerprints.txt lines: <name>|<path>|<body-fingerprint>|<note>
"""
import sys
import time
import urllib.request
import urllib.error


def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "cicd-exposure-check"})
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
                status, body = fetch(f"{scheme}://{host.rstrip('/')}{path}")
                time.sleep(0.3)
                if status is None:
                    continue
                unauth_ok = status == 200 and (not fp or fp.lower() in body.lower())
                login_wall = status in (401, 403)
                if unauth_ok:
                    print(f"{host}\tsystem={name}\tpath={path}\tstatus={status}\t"
                          f"access=UNAUTHENTICATED\tnote={note}")
                    break
                elif login_wall:
                    print(f"{host}\tsystem={name}\tpath={path}\tstatus={status}\t"
                          f"access=gated\tnote=present-but-gated (fingerprinting only, no login attempted)")
                    break


if __name__ == "__main__":
    main()
