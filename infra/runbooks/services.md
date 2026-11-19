# Runbook: exposed services / panels

Probe in-scope hosts for the paths in payloads/panels.txt with read-only GETs.
- 200 + an unauthenticated panel/tool = finding (exposure). Record host+path+what it is.
- 401/403 = present but gated; note it, not a finding alone.
- .git exposure (/.git/config, /.git/HEAD returning 200) = source disclosure; high value.
Never log in (not even default creds), never brute force, never interact beyond confirming
exposure. Exposure is the finding, not what you can do once inside.
