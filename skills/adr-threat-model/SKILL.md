---
name: adr-threat-model
description: Drafts Architecture Decision Records (ADRs) with complete STRIDE threat models in the aegis-forge format. Use before writing code for any new module, endpoint, trading strategy, or technology adoption — and whenever asked to create/review an ADR or threat model under docs/adr/.
---

# ADR & Threat Model Generator

Every non-trivial change in an aegis-forge project is preceded by a STRIDE
threat model documented as an ADR. Source of truth: `docs/adr/ADR-000-template.md`
(format) and `docs/adr/ADR-001-Threat-Modeling-Standard.md` (standard).
ADRs are machine-validated by `scripts/validate_adrs.py` — output that fails
validation is defective.

## Mandatory Structure (validator-enforced)

1. **Metadata table** with `ID`, `Title`, `Status`, `Date`.
2. **Status** ∈ {`PROPOSED`, `ACCEPTED`, `DEPRECATED`, `SUPERSEDED`}.
3. A **Context/Problem** section.
4. A **Decision/Consequences** section.
5. A **complete STRIDE table** — all six categories, each threat mapped to a
   concrete control (see below).

## The STRIDE Table (all six rows required)

| Category | Guiding question | Example control |
|---|---|---|
| **S**poofing | Can identity be faked? | OIDC/OAuth2, mTLS, HMAC-signed webhooks |
| **T**ampering | Can data be modified undetected? | Append-only audit tables, anti-tamper triggers, checksums |
| **R**epudiation | Can an actor deny their action? | Immutable audit trail with actor + timestamp + correlation ID |
| **I**nformation Disclosure | Can secrets/PII leak? | Anti-PII logging, AES-256 FLE, least-privilege IAM |
| **D**enial of Service | Can the service be exhausted? | Rate limiting, circuit breakers, kill-switch |
| **E**levation of Privilege | Can a role gain more power? | Server-side RBAC, maker-checker, SoD, IDOR ownership checks |

Each threat row MUST name a **specific, verifiable control** — "use encryption"
is not a control; "AES-256-GCM field-level encryption on `tokens` table, keys
from Keystore" is.

## Procedure

1. Identify the component's trust boundaries (client↔API, API↔DB, app↔broker).
2. Enumerate threats per boundary using the six STRIDE questions.
3. Map every threat to a control that already exists in the baseline or is
   explicitly decided in this ADR.
4. Record rejected alternatives and *why* (the "Consequences" half of the
   Decision section).
5. Place the file at `docs/adr/ADR-NNN-<slug>.md` (next free number; skip
   `ADR-000` which is the template).
6. Verify locally: `python scripts/validate_adrs.py` must exit 0.

## Anti-Patterns to Refuse

- ADRs written *after* the code (threat modeling is a gate, not a memo)
- STRIDE tables with empty or "N/A" cells without a documented justification
- Controls that are aspirational ("we should add rate limiting") instead of
  decided and verifiable
- Missing Status transitions — when superseded, link old ↔ new ADR IDs
