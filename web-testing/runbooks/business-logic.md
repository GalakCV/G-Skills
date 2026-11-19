# Technique: business logic

The bugs SAST and scanners miss: flaws in how the application's rules work, not in a sink.
They need understanding the app's intent — and careful, non-destructive testing.

## Where they live
- Workflow/state machines: skip a step, repeat a one-time step, reach a later state
  without the earlier one (checkout without payment, approve your own request).
- Price/quantity/amount tampering: negative quantities, zero/negative price, currency or
  decimal manipulation, coupon stacking, rounding abuse.
- Trust boundaries: a value the client controls that the server should recompute (totals,
  roles, discounts, "is_admin" flags in requests).
- Rate/limit bypass: a cap enforced client-side only, or resettable.
- Race conditions (TOCTOU): a check and an action with a gap — double-spend a credit, use a
  one-time token twice. Test with a small number of near-simultaneous requests, NON-
  destructively, on your own test resources only.

## How to test (carefully)
- Map the intended flow first (as a normal user). The bug is a deviation from intent, so
  you must know the intent.
- Tamper one variable at a time; observe whether the server accepts a state it shouldn't.
- Use YOUR OWN test accounts/resources. Never manipulate real orders, balances, or other
  users' state to prove a logic flaw.

## Non-destructive proof
- Prove the flaw with the smallest possible effect on your own test data: one order placed
  at a wrong price, one token reused once. Do NOT scale it, do not profit from it, do not
  touch production/other-user data.

## Confirm & report
- Evidence: the intended flow vs the request sequence that broke it, and the server
  accepting the invalid state. There's often no single CWE — describe the rule violated and
  the business impact (financial, privilege, data) concretely. State the preconditions.
