# Contributing to Aegis Forge

Thank you for helping improve this baseline. This document explains how to propose changes so they land quickly, safely, and consistently — whether you are a human or directing an AI agent.

---

## 1. Ground Rules

1. **Specification-first.** Every change traces back to a spec in `docs/` (PRD, OpenAPI, schema, blueprint). Don't add code without a corresponding spec or doc update.
2. **Secure-by-design.** Follow `SECURITY.md`, the threat-modeling mandate (`docs/adr/ADR-001`), and the four pillars in `AGENTS.md`. No secrets in code, commits, or logs.
3. **Quality gates are mandatory.** A change merges only when all CI checks pass (see `docs/testing-strategy.md` §4). "It works on my machine" is not a merge criterion.
4. **Small, focused PRs.** One concern per PR. Large refactors are split into reviewable steps.

---

## 2. Development Setup

Choose one:

- **Dev Container (recommended):** open in VS Code → *"Reopen in Container"* (or use GitHub Codespaces). Toolchain is pre-installed and pinned (`.devcontainer/`).
- **Manual:** see `SETUP.md` for Python, Node, Docker, gitleaks, and pre-commit installation.

Enable local hooks so you catch issues before CI:
```bash
pre-commit install        # hygiene, gitleaks, lint, contract checks
```

---

## 3. Branching & Workflow

1. Branch from `main`: `git checkout -b <type>/<short-desc>` (e.g., `feat/rate-limiting`, `fix/jwt-refresh`, `docs/runbook`).
2. Make changes with tests at the right layer (`docs/testing-strategy.md`).
3. Keep commits clean and logical (see §4).
4. Open a Pull Request; fill in the template; link the related issue/spec.
5. Address review feedback; keep the branch up to date with `main` (rebase preferred).

**Protected branch:** `main` requires PR review (incl. CODEOWNERS) and green status checks (`SETUP.md` §6). No direct pushes to `main`.

---

## 4. Commit Convention — Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) so history is readable and **release-please** can automate versioning/changelogs.

```
<type>(<optional scope>): <imperative summary>

<optional body — what & why, not how>

<optional footer — BREAKING CHANGE: ..., Refs: #123>
```

**Types:** `feat` (new capability → minor), `fix` (bug fix → patch), `docs`, `ci`, `chore`, `refactor`, `perf`, `test`, `build`, `style`, `revert`.

**Rules:**
- Imperative, present tense, ≤ 72 chars in the summary (`add`, not `added`/`adds`).
- Use a scope when helpful: `feat(auth):`, `fix(api):`, `docs(backend):`.
- Mark breaking changes with `!` or a `BREAKING CHANGE:` footer → triggers a **major** bump.

Examples from this repo:
```
feat(agents): add gated playbooks, prompt library, and output-quality evals
docs(backend): add backend checklist, observability, migrations, and ADR-002
ci(security): add pre-commit parity, CODEOWNERS, and harden security workflow
```

---

## 5. Pull Request Requirements

A PR is merge-ready when it has:

- [ ] A clear title + description (what, why, how verified).
- [ ] Tests added/updated at the appropriate layer; **coverage ≥ 80%** on changed code.
- [ ] All CI gates green (security, contract, tests, build).
- [ ] Docs updated for any behavior/spec change (README, relevant `docs/`).
- [ ] **An ADR** for any architectural decision, new feature/module/endpoint, or schema change — format per `docs/adr/ADR-000-template.md`, STRIDE-complete (enforced by the `adr-validation` workflow).
- [ ] CODEOWNERS approval for the areas touched (`.github/CODEOWNERS`).
- [ ] No secrets, no PII, no `console.log`/debug leftovers.

---

## 6. Code Review Expectations

**As an author:** keep PRs small; respond to feedback; explain non-obvious choices; mark threads resolved when addressed.

**As a reviewer:** review for correctness, security (authz, injection, secrets), contract compliance, test coverage, and clarity. Be specific and kind. Approve only when gates pass and concerns are addressed.

---

## 7. Documentation Standards

- Language: **English**, plain and direct (no buzzwords/clichés).
- Templates live in `docs/` (`PRD-template.md`, `ADR-000-template.md`, `runbook-template.md`, etc.) — copy, don't edit the template for project-specific content.
- Register any **new** reference doc in the `AGENTS.md` Mandatory Reference table and the `README.md` structure tree.
- ADRs are immutable once ACCEPTED; supersede with a new ADR rather than rewriting history.

---

## 8. Reporting Issues & Security

- **Bugs / features:** open a GitHub Issue with reproduction steps and expected vs actual behavior.
- **Security vulnerabilities:** **do not** open a public issue — follow `SECURITY.md` (private disclosure).

---

## 9. License

By contributing, you agree your contributions are licensed under the project's **Apache-2.0 License** (`LICENSE`).
