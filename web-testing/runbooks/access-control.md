# Technique: access control (IDOR / BOLA / privilege / forced browsing)

Highest-yield, lowest-noise class. Most findings need only a second account and a swapped
identifier. All read-first; never modify another user's data to "prove" it.

## Setup
- Two identities where possible: a low-privilege user A and a second user B (and an
  unauthenticated session). Keep their IDs/tokens separate.
- Map object references in the app: numeric IDs, UUIDs, slugs, filenames, account numbers
  in URLs, bodies, and headers.

## IDOR / BOLA (object-level)
- As user A, access an object that belongs to user B by swapping the identifier
  (`/api/orders/1001` → `1002`; `?userId=A` → `B`).
- Read the result: A's data (expected) vs B's data (broken object authorization).
- Numeric sequential IDs are highest-risk; UUIDs harder but still test (leaked IDs, lower
  entropy). Test GET first; a read IDOR is enough to report.
- Prove with exactly ONE other object you're authorized to compare. Do not iterate the
  full range or pull real users' records.

## BFLA (function-level)
- Call an admin/privileged action as a low-priv user (endpoint found in JS, spec, or docs).
  Does it execute, or return 403? Test the method too (POST blocked but PUT allowed?).

## Missing authorization (the incomplete-fix pattern)
- When a security fix added a permission check to one method, check its SIBLINGS for the
  same data. A method that returns the same sensitive data without the check is a real
  finding — cite the fix commit as evidence the data is meant to be gated.

## Forced browsing / horizontal & vertical
- Access staff/admin paths as a normal user; access another tenant's resource in a
  multi-tenant app. Observed data you shouldn't see = finding.

## Confirm & report
- Evidence: the request as user A + the response containing B's (or privileged) data, both
  minimally redacted. State the preconditions (authenticated? which role?). CWE-639/CWE-285/
  CWE-862. Stop once proven — do not enumerate further.
