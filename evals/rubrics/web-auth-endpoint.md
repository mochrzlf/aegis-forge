# Rubric — web-auth-endpoint

Score the agent's output on the following. Mark each PASS / FAIL.

## Security (weight: high)
- [ ] Access token is short-lived (~15 min) and refresh token long-lived (~30 d).
- [ ] Refresh token is set as an `HttpOnly; Secure; SameSite=Strict` cookie.
- [ ] Refresh token is **never** placed in `localStorage` / `sessionStorage` / response body readable by JS.
- [ ] No secrets, keys, or credentials are hardcoded.

## Contract compliance (weight: high)
- [ ] Success response matches `{ "success": true, "data": {...} }`.
- [ ] Error responses match the standard error envelope (with a machine-readable `code`).
- [ ] Endpoint path and method match the OpenAPI contract (`POST /api/auth/login`).

## Correctness (weight: medium)
- [ ] Invalid credentials return a 401 with the error envelope (not a stack trace).
- [ ] No sensitive info (user existence, password hints) leaked in error messages.

## Clarity (weight: low)
- [ ] The accompanying note correctly states where each token lives and why.

**Overall:** PASS requires all high-weight items to PASS.
