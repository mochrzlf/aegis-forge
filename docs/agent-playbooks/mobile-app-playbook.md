# Mobile Application Playbook

> Follow the phases in order. Each phase is a **gate** — do not proceed until its verification checklist passes. Reference: `docs/blueprints/mobile-application-blueprint.md` + `docs/security/mobile-security-checklist.md`.

---

## PHASE 0 — Context Load
1. Read `AGENTS.md` in full.
2. Read `docs/blueprints/mobile-application-blueprint.md`.
3. Read `docs/security/mobile-security-checklist.md` and `docs/diagrams/mobile-auth-sequence.md`.

**✅ Verify:** You can state the storage rule (Android Keystore / `EncryptedSharedPreferences`, never plain `SharedPreferences`) and the SSL-pinning + `FLAG_SECURE` requirements.

---

## PHASE 1 — Specify
1. Draft `docs/PRD.md` and `docs/PRD-detail.md` (personas, offline behavior, platform targets Android/iOS).

**✅ Verify:** Stories specify offline/online behavior and which screens are sensitive (require `FLAG_SECURE`).

---

## PHASE 2 — Threat Model
1. New ADR in `docs/adr/` with STRIDE, focused on mobile: token theft from insecure storage, MITM (no pinning), screenshot/shoulder-surfing, rooted/jailbroken device, insecure deep links.

**✅ Verify:** Each mobile threat maps to a concrete control (Keystore, pinning, `FLAG_SECURE`, root detection stance).

---

## PHASE 3 — Contract (API)
1. Define `docs/openapi.yaml` for all backend endpoints the app consumes.
2. Confirm token lifecycle matches `docs/diagrams/mobile-auth-sequence.md`.
3. Start the mock server (`make mock-api`, port 4010) so the app can be built before the backend.

**✅ Verify:** OpenAPI lints clean; mock server returns contract-shaped responses the app can consume (use `10.0.2.2:4010` on Android emulator).

---

## PHASE 4 — Design
1. Produce `docs/ui-design.md` (tokens, typography, spacing, dark mode).
2. Optionally use `ui-ux-pro-max` with `--stack jetpack-compose` / `--stack swiftui` / `--stack flutter` / `--stack react-native`.

**✅ Verify:** Tokens map to the target platform's theming; touch targets & accessibility sizes stated.

---

## PHASE 5 — Implement
1. Scaffold per Clean Architecture (Kotlin + Jetpack Compose, or Flutter / React Native per blueprint).
2. Store tokens in `EncryptedSharedPreferences` (Android Keystore) / Keychain (iOS).
3. Enforce HTTPS + SSL pinning in network config.
4. Apply `FLAG_SECURE` on sensitive screens.

**✅ Verify:** No secrets/tokens in plain storage; pinning active; sensitive screens block screenshots; app runs against the mock API.

---

## PHASE 6 — Verify
1. Unit tests + at least one instrumented/UI test of the auth flow.
2. Walk `docs/security/mobile-security-checklist.md` line by line.
3. Run `make audit` (Gitleaks clean — no keystores, `google-services.json`, or API keys committed).

**✅ Verify:** Checklist items pass; no mobile secrets in Git; auth flow works against mock then real API.
