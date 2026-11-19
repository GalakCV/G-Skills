# Technique: mass assignment (over-posting)

The API binds request fields straight to an object, so you set fields the server should
never accept — `role`, `is_admin`, `verified`, `balance`, `price`, `owner_id`. Test on
your own account/objects; never escalate against real data.

## Find the candidates
- From the spec's schemas and the object's GET response: every field the object HAS.
- Compare with what the create/update endpoint DOCUMENTS as settable. The gap — fields the
  object has but the write endpoint doesn't advertise — is the mass-assignment surface.
- High-value fields: `role`, `isAdmin`, `is_staff`, `verified`, `emailVerified`, `status`,
  `balance`, `credits`, `price`, `discount`, `owner`, `tenantId`, `id`.

## The test (on your own object)
- On a create/update you're authorized to make, ADD a privileged field to the body:
  `{"name":"x","role":"admin"}` or `{"verified":true}` / `{"balance":99999}`.
- Read the result: does the GET of your object now reflect the injected value? Did your
  own account's role/flag actually change?
- Prove it on YOUR account only. Do not set another user's owner_id, do not grant yourself
  access to real resources beyond showing the field was accepted.

## Nested & alternate forms
- Nested objects (`{"profile":{"role":"admin"}}`), arrays, and JSON vs form encoding — the
  binder may accept one and filter another.
- `PATCH` vs `PUT` may bind differently.

## Confirm & report
- Evidence: the request with the extra field + the object reflecting it (your own object).
  State what privilege/flag it changed and the impact if abused (privilege escalation,
  financial). CWE-915 / OWASP API6. Revert any change you made to your test object and note
  that you did.
