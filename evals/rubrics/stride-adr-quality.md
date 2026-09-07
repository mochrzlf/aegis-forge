# Rubric — stride-adr-quality

Score the agent's STRIDE ADR. Mark each PASS / FAIL.

## STRIDE coverage (weight: high)
- [ ] All six categories are addressed: **S**poofing, **T**ampering, **R**epudiation, **I**nformation Disclosure, **D**enial of Service, **E**levation of Privilege.
- [ ] Each category has at least one threat that is **specific to the feature** (user authentication), not a generic restatement of the category name.

## Threat → Control mapping (weight: critical)
- [ ] Every identified threat is paired with a **concrete, actionable** control (e.g., "rate-limit login attempts", "HttpOnly SameSite cookie", "bcrypt/argon2 hashing", "audit-log auth events"), not a vague note like "handle securely".
- [ ] Controls reference the baseline's own standards where applicable (cookie rules, IAM policy, audit trail).

## ADR structure (weight: medium)
- [ ] Follows `docs/adr/ADR-000-template.md` structure (title, status, context, decision, consequences).
- [ ] Has a unique ADR number and clear status (e.g., Proposed/Accepted).

## Realism (weight: medium)
- [ ] No control contradicts the baseline (e.g., does NOT suggest storing tokens in localStorage).
- [ ] Prioritization or residual-risk note is present.

**Overall:** PASS requires ALL critical-weight items to PASS and at least one specific threat per STRIDE category.
