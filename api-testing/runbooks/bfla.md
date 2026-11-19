# Technique: BFLA (broken function-level authorization)

A low-privilege user invokes a privileged FUNCTION they shouldn't (OWASP API5). Where BOLA
is about objects, BFLA is about actions/endpoints. Read-first; prove write-side authz on
your own test resources only.

## Find privileged functions
From the spec, JS, or docs: admin endpoints, user-management, config, role changes,
export, delete-all, impersonation, feature flags. Note the method (often POST/PUT/DELETE)
and the role they imply.

## The test
- As a **low-privilege** user (or the wrong role), call the privileged endpoint.
  - Read-only privileged function (admin list, config read) → GET it, see if it returns.
  - State-changing privileged function → test authorization WITHOUT causing real impact:
    prefer your own test object, or send the request and read whether the server returns
    403 (blocked) vs 200/accepted — but do NOT complete a destructive action against real
    or other-user data to "prove" it. If the only way to prove is destructive, STOP and get
    human approval; often the 403-vs-200 response on a benign/own object is enough.

## Method & path tricks (authz often keyed wrong)
- Same path, different verb: GET gated but PUT/DELETE not.
- Admin path reachable under a non-admin route, alternate casing, or an undocumented
  sibling (the incomplete-fix pattern — one method hardened, a sibling left open).
- Role in a client-controlled field the server trusts.

## Confirm & report
- Evidence: the privileged request as a low-priv identity + the server accepting it (or
  returning data it shouldn't), on a benign/own resource. CWE-862 / OWASP API5.
  Preconditions: which (low) role. Never demonstrate by harming real data — the authorization
  gap is the finding, not the damage.
