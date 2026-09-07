# Rubric — api-contract-envelope

Score the agent's OpenAPI output. Mark each PASS / FAIL.

## Envelope compliance (weight: high)
- [ ] Every success response matches `{ "success": true, "data": {...} }`.
- [ ] Every error response matches the standard error envelope with a machine-readable `code` and human-readable `message`.
- [ ] No endpoint returns a bare/raw payload bypassing the envelope.

## Pagination (weight: high)
- [ ] The list endpoint (`GET /api/users`) returns a `meta` object with `page`, `per_page`, and `total`.
- [ ] Pagination query params (`page`, `per_page`) are documented as parameters.

## Security (weight: high)
- [ ] A security scheme (bearer/cookie) is declared under `components.securitySchemes`.
- [ ] Protected endpoints reference the scheme via `security`.

## OpenAPI validity (weight: medium)
- [ ] Document is valid OpenAPI 3.x (would pass Redocly lint): has `openapi`, `info`, `paths`.
- [ ] Status codes cover success + at least one client error (4xx) and use standard response shapes.

## Clarity (weight: low)
- [ ] Schemas are named and reused via `$ref` rather than duplicated inline.

**Overall:** PASS requires all high-weight items to PASS.
