# Performance Budgets

> **Purpose:** Set explicit, machine-enforceable limits for frontend performance so regressions are caught in CI — not by users. Complements `docs/frontend-checklist.md` §3 (what to optimize) with **how much is allowed**.
>
> A **budget exceeded = build fails**. Budgets are a contract, not a guideline.

---

## 1. Core Web Vitals Targets (p75, field data)

| Metric | Good ✅ | Needs Improvement ⚠️ | Poor ❌ | **Budget (block above)** |
|---|---|---|---|---|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s | **≤ 2.5s** |
| **INP** (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms | **≤ 200ms** |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 | **≤ 0.1** |
| TTFB | ≤ 800ms | ≤ 1.8s | > 1.8s | ≤ 800ms |
| FCP | ≤ 1.8s | ≤ 3.0s | > 3.0s | ≤ 1.8s |

> INP replaced FID as a Core Web Vital (March 2024) — optimize for **interaction responsiveness**, not just first input.

---

## 2. Resource Budgets (per page/route)

| Resource | Budget (compressed) | Notes |
|---|---|---|
| **Total JS** | **≤ 200 KB** gzip | Initial bundle; code-split the rest |
| Route-level JS | ≤ 100 KB gzip | Per lazy-loaded route |
| **Total CSS** | ≤ 50 KB gzip | Tailwind purged output |
| Fonts | ≤ 100 KB, ≤ 2 families | `font-display: swap`; subset glyphs |
| **Hero/LCP image** | ≤ 100 KB | AVIF/WebP, responsive `srcset` |
| Total images (above fold) | ≤ 500 KB | Lazy-load below the fold |
| **Total page weight** | ≤ 1 MB | First load, compressed |
| Requests | ≤ 50 | First load |
| Third-party JS | ≤ 100 KB | Audit ruthlessly — see §6 |

> These are **starting defaults**; tighten per product. A data-dense trading dashboard may need a higher charting budget — set it explicitly, don't silently blow past.

---

## 3. Lighthouse CI Budgets (assert in CI)

`lighthouserc.json` — run against key routes on every PR:

```json
{
  "ci": {
    "collect": { "url": ["/", "/login", "/dashboard"], "numberOfRuns": 3 },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 0.95 }],
        "categories:best-practices": ["error", { "minScore": 0.95 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 1800 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "interactive": ["error", { "maxNumericValue": 3800 }],
        "total-byte-weight": ["error", { "maxNumericValue": 1048576 }]
      }
    }
  }
}
```

---

## 4. Bundle-Size Enforcement

### bundlesize / size-limit (fail the build)
```json
// package.json — size-limit
"size-limit": [
  { "path": ".next/static/chunks/main-*.js", "limit": "200 KB" },
  { "path": ".next/static/css/*.css",        "limit": "50 KB"  }
]
```
```bash
npx size-limit        # exit 1 if any budget exceeded -> block merge
```

### Track over time
- Use **bundle analysis** (`@next/bundle-analyzer` / `rollup-plugin-visualizer`) on every build; store the report as a CI artifact.
- Alert if the main bundle grows **> 5%** vs `main` — a PR must justify its size.

---

## 5. Backend / API Performance Budgets (context)

Frontend speed depends on backend latency — set server budgets too (see `docs/backend-checklist.md` §5 and `docs/observability.md`):

| Metric | Budget |
|---|---|
| API p50 latency | ≤ 100ms |
| API p95 latency | ≤ 300ms |
| API p99 latency | ≤ 800ms |
| DB query p95 | ≤ 50ms |
| Error rate | < 0.1% |

---

## 6. Third-Party & Runtime Discipline

- [ ] **Audit every third-party script** — analytics, chat, tag managers. Each costs JS + main-thread time. Remove or lazy-load anything non-essential.
- [ ] Load third parties with `async`/`defer` or `next/script` `strategy="lazyOnload"`.
- [ ] Long tasks: keep main-thread tasks **< 50ms**; break up with `scheduler.yield()` / web workers.
- [ ] Avoid large client-side state hydration; prefer server components / streaming where the framework supports it.

---

## 7. Enforcement & Workflow

1. **Local:** `npx size-limit` + Lighthouse in dev before pushing.
2. **CI:** Lighthouse CI + size-limit run on every PR; **budget exceeded → merge blocked**.
3. **Field monitoring:** collect real-user CWV (e.g., `web-vitals` → analytics/OTel) to confirm lab numbers; alert when p75 regresses (see `docs/observability.md`).
4. **Exceptions:** to exceed a budget, open a PR that **raises the number in this file + config with a written justification** — never bypass silently.

---

## 8. Setup Checklist

- [ ] `lighthouserc.json` (or equivalent) configured with the budgets above.
- [ ] `size-limit`/`bundlesize` wired into CI and set to **error** on exceed.
- [ ] Bundle analyzer report generated per build.
- [ ] `web-vitals` real-user reporting instrumented.
- [ ] CWV + resource budgets documented per product (this file is the default).
- [ ] Third-party scripts audited and lazy-loaded.
