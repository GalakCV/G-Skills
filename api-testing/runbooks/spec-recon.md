# Technique: spec recon (mine the API surface)

Find and mine the API's own description. A spec is a treasure map: the full surface, the
auth model, and where the weak points are — without guessing. The spec itself is intel,
not a bug (exposing it is low/info).

## Find the spec
- Common paths: `/openapi.json`, `/swagger.json`, `/swagger/v1/swagger.json`,
  `/api-docs`, `/v3/api-docs`, `/openapi/v3.json`, `/api/swagger.json`, `/graphql`
  (introspection), `/.well-known/`.
- Also: JS bundles referencing API bases, `/swagger-ui`, Postman collections, doc portals.

## Mine it (parse the file, don't re-hit the host)
From an OpenAPI/Swagger JSON:
- **Endpoints + methods**: the full path list and verbs.
- **Endpoints declared WITHOUT auth**: operations overriding global `security` with
  `security: []`, or missing it entirely. Cross-reference with the Bearer-protected ones —
  that's where missing-auth lives.
- **Path params = BOLA candidates**: paths with `{id}`, `{userId}`, `{uuid}`.
- **Interesting by name**: admin, internal, export, debug, token, key, config, upload, user.
- **Servers block**: other hostnames/environments (prod, internal URLs) leaked.
- **Schemas / field names**: the data model, PII fields, and hidden params not in the UI
  (feeds mass-assignment testing).
- **Security schemes**: the auth model (OAuth flows, token URL, scopes).

For GraphQL: run introspection (if enabled) to get the full type/query/mutation map;
note queries that expose sensitive types and mutations that change state.

## Hand off
Produce the ranked test list: no-auth-declared GETs (→ auth-enforcement),
Bearer-protected GETs (→ auth-enforcement no-token test), id-param endpoints (→ bola),
privileged actions (→ bfla), rich write schemas (→ mass-assignment). Never claim a bug
from the spec alone — it tells you WHERE to test, not that something is broken.
