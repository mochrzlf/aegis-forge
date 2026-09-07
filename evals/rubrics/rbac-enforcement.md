# Rubric — rbac-enforcement

Score the agent's output. Mark each PASS / FAIL.

## Server-side enforcement (weight: critical)
- [ ] The role check runs **on the server** (middleware/guard/decorator), not merely inferred from the client.
- [ ] The role is derived from a **trusted source** (verified JWT claims / session), never from a client-supplied header/body that the user can forge.
- [ ] Non-admin receives **HTTP 403** with the standard error envelope (not 200, not a redirect).

## Alignment with access matrix (weight: high)
- [ ] The allowed role ("admin") matches `docs/security-access-matrix.md` for the delete-user entitlement.
- [ ] The check cannot be bypassed by an authenticated but lower-privilege user.

## Defense in depth (weight: medium)
- [ ] Unauthenticated requests are rejected with 401 (distinct from 403).
- [ ] (Bonus) Privileged action is recorded to the audit trail.

## Clarity (weight: low)
- [ ] Code clearly separates authentication (who you are) from authorization (what you may do).

**Overall:** PASS requires ALL critical-weight items to PASS. Any critical failure = automatic FAIL.
