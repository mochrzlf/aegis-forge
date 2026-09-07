# Frontend Testing Standard

> **Purpose:** Define the mandatory testing layers, tools, and coverage expectations for every frontend module (Web primary; mobile notes included) before it can be marked *Ready for Production*. Complements `docs/frontend-checklist.md` (what to verify) with **how to verify it automatically**.
>
> AI agents must scaffold these tests when generating a component or screen — tests are not an afterthought.

---

## 1. The Testing Pyramid (frontend)

```
        ┌─────────────┐
        │   E2E (few) │   Playwright — critical user journeys only
        ├─────────────┤
        │ Component   │   Vitest + Testing Library + axe-core
        │  (many)     │
        ├─────────────┤
        │  Unit (most)│   Vitest — pure logic, hooks, utils, stores
        └─────────────┘
```
**Ratio guide:** ~70% unit, ~25% component, ~5% E2E. E2E is expensive and flaky — reserve it for money-paths (auth, checkout, place-order).

---

## 2. Recommended Stack (web)

| Layer | Tool | Notes |
|---|---|---|
| Test runner | **Vitest** | Fast, Vite-native, Jest-compatible API |
| Component testing | **@testing-library/react** | Query by role/label, not implementation |
| Accessibility | **axe-core** (`vitest-axe` / `jest-axe`) | Automated a11y assertion per component |
| E2E | **Playwright** | Cross-browser, trace viewer, codegen |
| Visual regression | Storybook + Chromatic *(optional)* | Snapshot UI states |
| Coverage | **c8 / v8** via Vitest | Enforce thresholds in CI |

> Mobile equivalents — Android: **JUnit + Compose UI Test + Paparazzi** (screenshot); iOS: **XCTest + XCUITest**; Flutter: **flutter_test + golden files**.

---

## 3. What to Test at Each Layer

### Unit (Vitest)
- Pure functions, formatters, validators, reducers, custom hooks, state stores.
- Edge cases: empty, null, overflow, locale/number formatting, boundary values.
- ❌ Do NOT unit-test third-party libraries or trivial JSX.

### Component (Testing Library + axe-core)
- **Renders** with required props; handles loading / empty / error states.
- **Interaction:** click, type, keyboard (Tab/Enter/Space) — assert behavior, not internals.
- **Accessibility:** assert **no axe violations** on every rendered component (see §5).
- **Contract:** form validation messages, disabled states, role/aria attributes.

### E2E (Playwright)
- Critical journeys only: sign-up/login, password reset, create → read → update → delete of a core entity, payment/place-order.
- Run against a **mocked or staging backend** (see `docs/openapi.yaml` + Stoplight Prism on `:4010`).
- Tag with `@smoke` so CI can run a fast subset on every PR.

---

## 4. Minimum Expectations (Release Blockers)

A module is **NOT** production-ready unless ALL of these pass:

- [ ] **Coverage:** ≥ **80%** lines on changed/new code (enforced in CI, not aspirational).
- [ ] **Component a11y:** every interactive component passes `axe` with **0 violations**.
- [ ] **States covered:** loading, empty, error, and success states each have a test.
- [ ] **Critical journey E2E:** at least one `@smoke` Playwright path for the feature's money-path.
- [ ] **No `data-testid` over-use:** queries prefer role/label/text (accessibility-first selectors).
- [ ] **Deterministic:** no `sleep()`/fixed timeouts — use Playwright auto-wait / Testing Library `findBy*`.

---

## 5. Accessibility Test Pattern (axe-core)

```tsx
// Component.test.tsx
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'vitest-axe'
import { LoginForm } from './LoginForm'

expect.extend(toHaveNoViolations)

it('has no accessibility violations', async () => {
  const { container } = render(<LoginForm />)
  expect(await axe(container)).toHaveNoViolations()
})
```
> Wire this into a shared test setup so **every** component test gets an axe assertion by default. Manual keyboard + screen-reader checks remain required (see `frontend-checklist.md` §2) — automation catches ~40-50% of a11y issues, not all.

---

## 6. Playwright `@smoke` Pattern

```ts
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test'

test('@smoke user can log in', async ({ page }) => {
  await page.goto('/login')
  await page.getByLabel(/email/i).fill('user@example.com')
  await page.getByLabel(/password/i).fill('Secret123!')
  await page.getByRole('button', { name: /sign in/i }).click()
  await expect(page).toHaveURL(/dashboard/)
})
```
Run smoke on every PR; full E2E suite nightly. Use `playwright.config.ts` projects for chromium + mobile viewport.

---

## 7. Mocking & Test Data

- **Network:** mock at the network boundary with **MSW** (Mock Service Worker) or Playwright `route` interception — never mock fetch/axios deep in components.
- **Backend:** point E2E at the **Prism mock server** (`docs/openapi.yaml`, port `4010`) for contract-true responses.
- **Data:** use factories/builders for test fixtures; avoid giant shared fixtures.
- **Secrets:** tests use dummy credentials only — never real tokens (see `docs/security/secrets-rotation.md`).

---

## 8. CI Integration

- [ ] `vitest run --coverage` on every PR; fail below the 80% threshold.
- [ ] `axe` assertions are part of the unit/component job (no separate step needed).
- [ ] `playwright test --grep @smoke` on every PR; full suite on `main`/nightly.
- [ ] Coverage + Playwright HTML reports uploaded as CI artifacts.
- [ ] Flaky-test policy: a test that flakes twice is quarantined and fixed within the sprint — never silently retried forever.

---

## 9. Anti-Patterns (do NOT do these)

- ❌ Testing implementation details (component internal state, private methods).
- ❌ Asserting on CSS classes/selectors instead of accessible roles/labels.
- ❌ E2E for every minor flow (slow, brittle) — push coverage down the pyramid.
- ❌ `await page.waitForTimeout(3000)` — flaky; use auto-waiting assertions.
- ❌ Skipping a11y because "axe passed once" — assert it per component, continuously.
