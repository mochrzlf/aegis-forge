# Testing Strategy

> **Purpose:** One unified, cross-domain testing strategy for every project derived from this baseline — what to test, at which layer, with which coverage gate, and how it is enforced in CI. This is the **single entry point** that ties together `docs/frontend-testing.md`, `docs/backend-checklist.md`, the `evals/` harness, and the contract/security checks.
>
> Principle: **tests are a release gate, not an afterthought.** AI agents must scaffold tests alongside code (see `docs/agent-playbooks/`).

---

## 1. The Test Pyramid (all domains)

```
            ┌──────────────┐
            │  E2E (few)   │  Playwright / mobile E2E — critical journeys only
            ├──────────────┤
            │ Integration  │  API + DB + services, contract tests
            │  & Contract  │
            ├──────────────┤
            │ Component    │  UI components / service units with deps
            ├──────────────┤
            │  Unit (most) │  Pure logic, domain rules, utils
            └──────────────┘
```
**Ratio guide:** ~70% unit · ~20% component/integration · ~5% contract · ~5% E2E. Push coverage *down* the pyramid — E2E is slow and brittle, so reserve it for money-paths.

---

## 2. Test Types & When to Use Them

| Type | Scope | Web | Mobile | Trading EA | Backend |
|---|---|---|---|---|---|
| **Unit** | pure logic | Vitest | JUnit/XCTest/flutter_test | Python pytest (calc/risk) | pytest/JUnit |
| **Component** | single unit + deps | Testing Library | Compose UI Test | strategy module | service + test DB |
| **Contract** | API/schema adherence | OpenAPI lint + Schemathesis | vs Prism mock | order contract | OpenAPI + schema parse |
| **Integration** | multiple services | API+DB | API+DB | broker sandbox | DB, Redis, queue |
| **E2E** | full user journey | Playwright `@smoke` | XCUITest/Maestro | backtest run | critical flows |
| **Security** | abuse cases | Semgrep/ZAP | mobile AppSec | risk-limit enforcement | authz, injection |
| **Performance** | latency/load | Lighthouse/k6 | startup, jank | execution latency | k6/load |
| **Agent quality** | LLM output | — | — | — | `evals/` (promptfoo) |

---

## 3. Domain-Specific Standards

### Web / Fullstack
Follow `docs/frontend-testing.md`: Vitest + Testing Library + axe-core + Playwright. Coverage ≥ **80%** on changed code; **0 axe violations**; `@smoke` E2E on money-paths. Enforce budgets per `docs/performance-budgets.md`.

### Mobile (Android / iOS / Flutter / RN)
- **Unit:** business logic, view-models, formatters.
- **UI:** Compose UI Test / XCUITest / flutter_test golden files.
- **Contract:** run against the Prism mock (`docs/openapi.yaml`, port `4010`).
- **Security:** token storage uses Keystore/Keychain (never plain prefs) — see `docs/security/mobile-security-checklist.md`.

### Trading EA / Algorithmic
- **Unit:** indicator math, position sizing, risk calculations (pytest).
- **Backtest as test:** a strategy must pass the **5-gate anti-overfitting SOP** before "done" (see `docs/agent-playbooks/trading-ea-playbook.md`): PF > 1.5, MaxDD < 15%, Sharpe > 1.2, OOS degradation < 25%, and the risk gate enforced.
- **Risk-limit tests:** prove the circuit-breaker halts at the daily-loss threshold (see `docs/security/trading-risk-policy.md`). **Never** test with live capital — sandbox/paper only.

### Backend / Services
Follow `docs/backend-checklist.md`: contract compliance, authz (403 for wrong role), validation/rate-limiting, data integrity, observability. Integration tests run against containerized Postgres 16 + Redis 7 (`docker-compose.yml`).

---

## 4. Coverage & Quality Gates (Release Blockers)

A change may merge only if **all** applicable gates pass:

- [ ] **Coverage:** ≥ 80% lines on changed/new code (enforced in CI; not aspirational).
- [ ] **Contract:** OpenAPI lint clean + `schema.sql` parses (CI `contract-validation`).
- [ ] **Security:** gitleaks, Semgrep, Trivy, dependency-review — no high/critical.
- [ ] **Accessibility (UI):** 0 axe violations per interactive component.
- [ ] **Smoke E2E:** the feature's `@smoke` path passes.
- [ ] **Migrations:** reversible & zero-downtime-safe (`docs/migrations.md`).
- [ ] **Agent outputs:** prompts changed → `evals/` rubrics still pass.

> Flaky-test policy: a test that flakes **twice** is quarantined and fixed within the sprint — never retried into silence.

---

## 5. Test Data, Mocking & Environments

- **Mock at the network boundary** (MSW / Playwright route / Prism) — not deep in units.
- **Contract-true backend:** point integration/E2E at the Prism mock or a containerized stack, not production.
- **Factories/builders** for fixtures; avoid giant shared fixtures.
- **Secrets:** tests use dummy credentials only; never real tokens (`docs/security/secrets-rotation.md`).
- **PII:** test data must be synthetic — never copy production personal data into lower environments.

---

## 6. Agent Output Quality (`evals/`)

LLM/agent-generated code is itself tested. The `evals/` harness (promptfoo) scores agent outputs against rubrics for security & contract correctness (e.g., "no tokens in localStorage", "RBAC enforced server-side", "risk gate present"). **Critical-weight rubric failures auto-FAIL.** Run `evals/` whenever you change prompts in `docs/prompt-library.md` or agent playbooks.

---

## 7. CI Mapping

| CI job | Enforces |
|---|---|
| `security-audit` | gitleaks, Semgrep, Trivy |
| `contract-validation` | OpenAPI lint + schema parse |
| `dependency-review` | vulnerable/malicious deps (PR) |
| `unit/component tests` | coverage ≥ 80%, axe = 0 |
| `e2e (@smoke)` | critical journeys |
| `scorecard`, `sbom` | supply-chain posture |
| `adr-validation` | ADR format + STRIDE completeness |

---

## 8. Definition of Done (testing lens)

A feature is **Done** when: specs are written (PRD/OpenAPI/schema), tests exist at the right layers, all gates in §4 are green, and the change is observable (`docs/observability.md`). If any gate fails, the work is **not** done — regardless of how much code exists.
