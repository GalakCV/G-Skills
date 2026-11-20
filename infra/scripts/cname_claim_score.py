#!/usr/bin/env python3
"""Rank dangling-CNAME candidates by claim-likelihood — classification only, no new requests.

Takes `takeover_check.py`'s own tab-separated output and buckets it into:
  CLAIMABLE    — service is on the known-claimable list (S3, GitHub Pages, Heroku,
                 Azure, Fastly, Netlify, ...) AND the CNAME target itself is dangling
                 (doesn't resolve) or returns the service's "unclaimed" fingerprint.
  NOT-CLAIMABLE — service is known non-claimable by design (CloudFront almost always
                 requires the distribution to exist in *your* account to re-point;
                 a dangling CloudFront alias is usually just a deleted distribution,
                 not a takeover primitive) or is a shared/multi-tenant edge the
                 fingerprints list marks `claimable=no`.
  UNKNOWN      — matched a CNAME pattern but no http fingerprint confirmed and the
                 service isn't in either list; needs a human look before reporting.

This exists because field data shows CLOUDFRONT dangling CNAMEs dominate large recon
runs (187 of them in one Coca-Cola pass) and burying the 2-3 real candidates in that
noise is how real takeovers get missed or reported wrong. Ranking, not filtering —
every row from the input still appears in the output.

Usage: cname_claim_score.py <takeover_check_output.tsv> <takeover-fingerprints.txt>
"""
import sys


def load_claimable_map(path):
    m = {}
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) == 4:
            service, _cname_sub, _fp, claimable = parts
            m[service] = claimable.strip().lower() == "yes"
    return m


def parse_row(line):
    # host\tservice=X\tclaimable=Y\tdangling_cname=Z\tmatch=W
    out = {"host": None}
    parts = line.rstrip("\n").split("\t")
    if not parts:
        return None
    out["host"] = parts[0]
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k] = v
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    claimable_map = load_claimable_map(sys.argv[2])
    rows = []
    for line in open(sys.argv[1]):
        row = parse_row(line)
        if row and row.get("service"):
            rows.append(row)

    buckets = {"CLAIMABLE": [], "NOT-CLAIMABLE": [], "UNKNOWN": []}
    for row in rows:
        service = row.get("service", "")
        dangling = row.get("dangling_cname", "false").lower() == "true"
        known_claimable = claimable_map.get(service)
        if known_claimable is True and dangling:
            buckets["CLAIMABLE"].append(row)
        elif known_claimable is False:
            buckets["NOT-CLAIMABLE"].append(row)
        else:
            buckets["UNKNOWN"].append(row)

    for label in ("CLAIMABLE", "UNKNOWN", "NOT-CLAIMABLE"):  # most actionable first
        for row in buckets[label]:
            print(f"{label}\t{row['host']}\tservice={row.get('service','?')}\t"
                  f"dangling={row.get('dangling_cname','?')}\tmatch={row.get('match','?')}")

    print(f"# summary: {len(buckets['CLAIMABLE'])} claimable, "
          f"{len(buckets['UNKNOWN'])} unknown (needs a look), "
          f"{len(buckets['NOT-CLAIMABLE'])} not-claimable (e.g. dead CloudFront)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
