# Runbook: TLS

`scripts/tls_check.sh <host>`: reports cert subject/issuer/dates, SAN, and any weak
protocol (SSLv3/TLS1.0/1.1) that still connects. Report expired/mismatched certs and weak
protocol support. These are usually low severity unless they enable something concrete
(e.g. a mismatch enabling a confusion attack). Read-only.
