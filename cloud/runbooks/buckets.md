# Runbook: bucket exposure

1. Run `scripts/cloud_fingerprint.py` on recon hosts to learn the provider in use.
2. Run `scripts/bucket_check.sh <target> <run_dir>` to test candidate names (read-only).
3. Interpret:
   - `PUBLIC` = unauthenticated listing works. If the bucket is the target's, that's the
     finding. Capture the URL + the listing response (or one object name) as proof. STOP —
     do not download objects.
   - `EXISTS` (403) = bucket present but private. Note it; not a finding by itself.
4. Never write, overwrite, or delete any object. Never exfiltrate contents.
5. Ownership check: confirm the bucket belongs to the target before reporting (named after
   it, referenced by it, or in-account per the program). A same-named third-party bucket is
   out of scope.
