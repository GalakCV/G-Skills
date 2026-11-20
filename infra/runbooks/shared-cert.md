# Runbook: shared/mismatched TLS certificate (tenant bleed-through)

This is the class of bug behind a real field finding: a target's staging host answered
with a certificate issued for a completely unrelated third-party domain, revealing a
shared load balancer / reverse proxy / SaaS platform serving the wrong backend for that
SNI — a strong infra-misconfiguration signal, not just an expired-cert nitpick.

1. Run `scripts/shared_cert_check.py <hosts.txt> <target-apexes.txt>
   [known-shared-wildcards.txt]`.
2. Two issue types, read differently:
   - `cert-does-not-cover-host` — a plain mismatch. Often benign (default/fallback
     cert on a load balancer with no SNI match), but worth one more look if the host
     is otherwise interesting (gated, admin-sounding name).
   - `cert-names-unrelated-domain` — **this is the interesting one.** If the foreign
     name is clearly a different company (not a known shared-CDN wildcard, not an
     internal affiliate), it means the target's infrastructure is sharing a TLS
     termination point with someone else's app — a multi-tenant hosting/orchestration
     misconfiguration. Escalate autonomously (still active-safe, still one more
     read-only check): confirm the foreign domain really belongs to someone else by
     checking its own public presence (WHOIS-adjacent: does it look like a real,
     unrelated company's site?), and check whether the target's app is *also*
     reachable on the foreign domain's IP (would indicate the swap goes both ways).
3. Never probe the foreign domain itself beyond that one confirmation — it is out of
   scope for this engagement; the finding is "target's host serves a third-party cert",
   not an invitation to test the third party.
4. Allowlist CDN wildcards (`*.cloudfront.net`, `*.azureedge.net`, `*.fastly.net`, your
   target's own known shared-hosting platform) before reporting, to avoid flagging
   ordinary multi-tenant CDN certs as findings.
