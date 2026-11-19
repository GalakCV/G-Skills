# Runbook: cloud asset fingerprint

Run `scripts/cloud_fingerprint.py <hosts.txt>`; it labels each host AWS/GCP/Azure/unknown
from CNAME aliases and response headers (x-amz-*, x-goog-*, x-ms-*). Use the label to pick
the right bucket/asset checks. Unknown isn't "no cloud" — it may be behind a CDN; check the
origin if the program allows.
