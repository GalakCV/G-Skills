# Technique: BOLA (broken object-level authorization)

The #1 API risk (OWASP API1). An authenticated user accesses another user's object by
changing an identifier. Read-first; prove with one object, never enumerate.

## Setup
- Two test accounts: user A (yours) and user B (a second you control). Note the object IDs
  each legitimately owns.

## The test
- As user A (with A's token), request an object that belongs to **B** by swapping the id:
  `GET /api/v1/orders/{B_order_id}`, `/users/{B_id}/profile`, `?account={B_account}`.
- Read the result:
  - A's own data on A's id, B's data on B's id → **BOLA**: the server returns B's object to
    A without checking ownership.
  - 403/404 on B's id → object authz enforced.

## Where the id hides
Path params, query params, request body fields, headers (`X-Account-Id`), and nested JSON.
Test every object reference, not just the obvious URL id.

## Harder variants (still read-first)
- **UUIDs/opaque ids**: harder to guess but test with IDs you legitimately obtained (from
  B's session, from a listing, from a referrer). Guessability affects severity, not validity.
- **Nested / second-order**: an id accepted inside a sub-resource or a filter that the
  top-level check missed.
- **Mass object access**: a list endpoint that returns all objects instead of the caller's
  — confirm it returns another tenant's/user's data, then stop.

## Prove with ONE object — do not enumerate
Showing A can read ONE of B's objects is the finding. Never iterate the ID range, never
pull the dataset, never access real users' data at scale. One cross-account read, minimally
redacted, is the evidence.

## Confirm & report
- Evidence: A's request (A's token) returning B's object. State the id type and whether it
  was guessable or obtained. CWE-639 / OWASP API1. Preconditions: authenticated as a normal
  user. Stop at one proof.
