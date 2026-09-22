# Gap Analysis & Improvement Roadmap

**Tanggal audit:** 2026-09-21 · **Versi saat ini:** v0.1.6 · **Status:** Open — dikerjakan per gelombang.

> Audit full isi repo (170 file, 11.6k baris) + cross-check tiap klaim README/AGENTS.md terhadap kode nyata.
> File ini adalah TODO list resmi. Update kolom **Status** tiap selesai. Jangan hapus item — tandai ✅.

Legenda: ⬜ belum · 🔄 on-going · ✅ selesai · ⛔ ditolak/di-skip (tulis alasannya)

---

## ⚠️ Temuan Kritis #1 — Klaim vs Realitas Skeleton

README menjual **4 tipe project** (Web, Mobile, Trading, Enterprise), tapi yang punya skeleton runnable **hanya 2, keduanya web**:

| Domain | Blueprint doc | Skeleton kode | Status |
|---|---|---|---|
| Web (FastAPI) | ✅ `docs/blueprints/web-application-blueprint.md` | ✅ `templates/web-app/` | Satu-satunya yang "runtime-verified" |
| Web (Next.js+Supabase) | ✅ | ⚠️ `templates/web-app-nextjs-supabase/` | **Reference Only** — README-nya sendiri nyatain "never the recommended default" (nabrak Dependency Gate: vendor lock-in Supabase, replay detection gak ada) |
| Mobile (Android/iOS) | ✅ `docs/blueprints/mobile-application-blueprint.md` | ❌ **tidak ada** | Keystore, SSL Pinning, FLAG_SECURE, R8 = **naratif di docs doang**. Nol baris Kotlin/Swift |
| Trading EA | ✅ `docs/blueprints/ea-trading-blueprint.md` | ❌ **tidak ada** | Circuit breaker, lot sizing, no-withdrawal API key = naratif. Nol file `.mq5`, nol Python bridge |

**Dampak:** klaim "production-ready, security-first template" untuk Mobile & Trading adalah **unfulfilled promise**. Siapapun yang clone & pakai langsung kecewa.

---

## ⚠️ Temuan Kritis #2 — Skeleton Andalan Tidak Penuhi Doktrin Sendiri

`AGENTS.md` §3.2 + `docs/security-iam-policy.md` mewajibkan hal-hal di bawah. `templates/web-app/` **tidak memilikinya**:

| Wajib oleh doktrin | Ada di skeleton? | Bukti |
|---|---|---|
| Rate limiting / brute-force defense | ✅ **Gelombang 1 item 1.1 selesai** (sebelumnya ❌) | `app/core/ratelimit.py`; ADR-003. Klaim lama "Redis dipakai hanya untuk healthz ping" sudah tidak berlaku |
| MFA / 2FA / step-up auth | ❌ tidak ada | — |
| Password reset flow | ❌ tidak ada | — |
| Email verification | ❌ tidak ada | — |
| Account lockout | ❌ tidak ada | — |
| **JML Kill-Switch** | ❌ **tidak berfungsi** | Kolom `User.status` (active/suspended) ada di model, tapi transisi ke `suspended` **tidak me-revoke** refresh token aktif. `AGENTS.md` §3.2.1 mewajibkan ini |
| **Maker-Checker (Four-Eyes)** | ❌ **tidak ada** | Tabel `approval_requests` direferensikan di `docs/security-access-matrix.md` baris 99 ("Verify Maker-Checker transaction logs in the `approval_requests` table"), **tabel tersebut tidak ada di `schema.sql` maupun migration**. Dual control cuma doktrin |
| Step-up re-auth (financial mutation) | ❌ tidak ada | `security-iam-policy.md` §41 mewajibkan |

**Catatan:** RTR (refresh token rotation) + replay detection + descendant revocation **sudah benar diimplementasi** (`auth_service.py`, `RefreshToken.parent_id`), audit append-only via DB trigger juga benar (`0001_init.py`). Ini fondasi bagus — perlu dilengkapi, bukan dibongkar.

---

## ⚠️ Temuan Kritis #3 — "Runtime-verified" tapi Zero Test Files

- `templates/web-app/Makefile` punya target `test` ("Run backend tests (pytest)")
- `AGENTS.md` §5 mewajibkan unit + security test suite
- CI `skeleton-smoke-test.yml` menjalankan docker compose + curl flow (health/register/login/refresh/401) — **ini bagus dan nyata**
- Tapi: **`find` seluruh repo untuk `test_*.py` / `conftest.py` = hasil 0.** Tidak ada satu pun file test.

Evals di `evals/` menguji *kepatuhan AI terhadap rule*, bukan menguji kode skeleton. Dua hal berbeda.

---

## Gelombang 0 — Pembersihan Noise (⚡ cepat, risiko ~nol)

Tugas kecil yang bikin repo terlihat tidak rapi / menyesatkan.

| # | Tugas | File | Status |
|---|---|---|---|
| 0.1 | Hapus salah satu pasangan duplikat (md5 identik): `docs/schema.sql` == `docs/schema-template.sql`, dan `docs/openapi.yaml` == `docs/openapi-template.yaml`. `init-new-project.sh` menangani copy-nya, jadi file asli hanya nambah noise | `docs/*.sql`, `docs/*.yaml` | ✅ |
| 0.2 | Perbaiki comment rusak (bilingual teks menyampur jadi 1 baris) pada service `prism` | `docker-compose.yml:48` | ✅ |
| 0.3 | Hapus dead reference `README.id.md` dari init script (di-mask `2>/dev/null \|\| true`, file tidak pernah ada), atau buat file-nya | `scripts/init-new-project.sh` | ✅ |
| 0.4 | Root `make up` menyalakan 4 container (Postgres, Redis, Mailpit, Prism) **tanpa app service** → beri komentar bahwa ini untuk docs/mock-only | `Makefile:35-40`, `docker-compose.yml` | ✅ |
| 0.5 | Merge / close 5 PR dependabot yang menumpuk (bukan code change, cuma action version bumps) | PR #38–#42 | ✅ |
| 0.6 | Bongkar monolit `docs/PANDUAN-AWAM.md` (620 baris) → pindahkan materi security/IAM yang berbobot ke `docs/security-iam-policy.md` (sudah ada), sisakan pandangan umum saja | `docs/PANDUAN-AWAM.md` | ✅ |

**Selesai Gelombang 0 → lanjut Gelombang 1.** Jangan lompat dulu — noise cleanup bikin diff Gelombang 1 mudah di-review.

---

## Gelombang 1 — Tutup Lubang Skeleton Andalan (🔥 prioritas tertinggi)

Alasan ini didahulukan: (a) `templates/web-app` adalah **satu-satunya bukti nyata** klaim "security-first", (b) persis di area expertise Pakel (IAM/PAM lifecycle, JML, Maker-Checker) → margin kualitas paling tebal, (c) setiap item saat ini **membocorikan doktrin lo sendiri** — menutupnya = kredibilitas instan.

| # | Tugas | File yang akan tersentuh | Detail teknis | Status |
|---|---|---|---|---|
| 1.1 | **Rate limiter di `/auth/*`** | `app/core/ratelimit.py` (new), `app/api/auth.py` | Sliding window counter via Redis yang sudah ada (~30 baris, **tanpa library baru** — ganti klaim palsu "rate limiter" di README jadi nyata). Endpoint: login, register, refresh. Per-user + per-IP | ✅ 2026-09-21 — sliding-window ZSET; per-account 10 + per-IP 30 (login), per-IP 5 (register), per-IP 60 (refresh); `429` + `RATE_LIMITED` + `Retry-After`; ADR-003; self-check `backend/tests/check_ratelimit.py` + e2e 429 terverifikasi (fakeredis, tanpa DB) |
| 1.2 | **Account lockout** | `app/services/auth_service.py`, `app/api/auth.py` | Redis counter untuk login gagal → lock sementara. Audit-log setiap event lock/unlock. Opsi: unlock manual oleh admin (audit-logged) | ✅ 2026-09-21 — `app/core/lockout.py` (counter + self-expiring key, no migration); hanya AuthError UNAUTHORIZED yang dihitung; TTL counter di-set sekali (anti window-stretching); `423 LOCKED`; audit `user.locked` (email di-hash, anti-PII) + `user.unlock`; endpoint admin `POST /users/{id}/unlock`; ADR-004; self-check + e2e 423 terverifikasi (fakeredis) |
| 1.3 | **JML Kill-Switch** ⭐ | `app/services/auth_service.py`, `app/api/users.py` (endpoint status), migration baru | Kini `User.status` mati. Ubah: status → `suspended` ⇒ revoke semua `refresh_tokens` aktif (`revoked_at = now()`) + tolak login baru. Audit-log. **Ini signature move dari background IAM banking — harus jadi showcase, bukan TODO** | ✅ 2026-09-21 — `PUT /users/{id}/status` admin-only; satu bulk UPDATE scoped `user_id + revoked_at IS NULL` (idempotent, tidak bisa menyentuh user lain — diuji); login non-active sudah ditolak sebelumnya (FORBIDDEN); audit `user.status.X_to_Y` + reason di transaksi yang sama; guard anti-self-suspend; **tidak butuh migration** (kolom sudah ada sejak 0001); ADR-005; self-check pakai SQLite in-memory |
| 1.4 | **Maker-Checker endpoint** ⭐ | migration baru, `app/models/__init__.py`, `app/services/approval_service.py` (new), `app/api/approvals.py` (new), `docs/schema*.sql` | Tabel `approval_requests` sudah direferensikan `security-access-matrix.md` tapi tidak ada di schema. Buat: kolom `maker_user_id <> checker_user_id` (wajib beda orang), 1 endpoint contoh (role promotion, dual-control), audit-log approvals. Lanjutkan rantai Maker-Checker di audit trail | ✅ 2026-09-22 — migration `0002_approval_requests.py` (CHECK constraint `maker_user_id <> checker_user_id` di DB, bukan cuma di app); consumer pertama: role promotion via `POST /approvals/role-change` → `approve`/`reject`; maker tidak bisa jadi checker (3 lapis: service + RBAC + DB CHECK); self-target ditolak; 1 pending per target+action (`CONFLICT`); approval → role + revoke session di transaksi yang sama (anti privilege-creep); expired auto-close + audit; audit `approval.requested/approved/rejected/expired`; ADR-006; self-check `backend/tests/check_approvals.py` (9 invarian) |
| 1.5 | **Password reset + email verification** | migration baru, `app/services/auth_service.py`, `app/api/auth.py` | Token table baru (reuse pola refresh-token: hash server-side SHA-256, expiry, single-use). 2 endpoint: request reset, confirm reset. Jangan log PII | ⬜ |
| 1.6 | **MFA / TOTP step-up** | `app/services/mfa_service.py` (new), `app/api/auth.py`, frontend | Paling berat, taruh terakhir di gelombang ini. TOTP via `pyotp` + backup codes (hash). Step-up untuk financial mutation per `security-iam-policy.md` | ⬜ |

---

## Gelombang 2 — Validasi Klaim "Tested" (🔨 jujurkan label)

| # | Tugas | File | Status |
|---|---|---|---|
| 2.1 | Test suite pertama untuk `templates/web-app` | `tests/` (new) | Kasus wajib: RTR replay detection → revoke descendants; RBAC 403; audit trigger menolak UPDATE/DELETE; rate limiter ter-trigger; JML kill-switch efektif; Maker-Checker menolak self-approve | ⬜ |
| 2.2 | Pisahkan `requirements-dev.txt` (pytest, testcontainers) agar image produksi tetap ramping | `templates/web-app/backend/` | ⬜ |
| 2.3 | Tambah job pytest di CI yang sudah ada (path-filtered, sama polanya) | `.github/workflows/skeleton-smoke-test.yml` | ⬜ |
| 2.4 | Ubah label "runtime-verified" di README menjadi akurat: "CI smoke-tested (docker), unit tests added in v0.X" | `README.md` | ⬜ |

---

## Gelombang 3 — Bayar Janji Mobile + Trading (🏗️ berat, payoff terbesar)

Ini klaim terbesar README yang belum ada kodenya. Kerjakan **Trading dulu** (blueprint 143 baris sudah detail, expertise tersedia) sebelum Mobile.

| # | Tugas | Struktur target | Detail | Status |
|---|---|---|---|---|
| 3.1 | **Skeleton Trading EA** | `templates/trading-ea/` (new) | (a) Python FastAPI bridge module; (b) risk-guardian: circuit breaker (close-all + cancel pending + pause hingga rollover + alert), dynamic lot sizing max 1-2% equity per trade, spread/slippage filter; (c) **satu file `.mq5` EA template beneran** (bukan hanya doc); (d) validasi API key no-withdrawal saat startup → refuse jika melanggar | ⬜ |
| 3.2 | **Skeleton Android** | `templates/mobile-android/` (new) | Kotlin: Keystore wrapper + EncryptedSharedPreferences, `network_security_config.xml` (SSL pinning), base Activity dengan `FLAG_SECURE`, R8/ProGuard config. iOS deferred (pertimbangkan Flutter/KMP bila perlu) | ⬜ |
| 3.3 | **Update init script** — saat `TYPE=mobile`/`trading`/`fullstack`, tawarkan skeleton seperti web (saat ini hanya web yang mendapat interaktif skeleton copy) | `scripts/init-new-project.sh`, `scripts/init-new-project.ps1` | ⬜ |
| 3.4 | CI smoke test untuk skeleton baru (mulai dari yang termurah: import/lint/build, bukan full docker) | `.github/workflows/` | ⬜ |

---

## Gelombang 4 — Rapikan Klaim Pemasaran (⚡ setelah 3 selesai)

| # | Tugas | File | Status |
|---|---|---|---|
| 4.1 | Tambah **tabel maturity per domain** di README — jujur: Web = code-backed & CI-tested; Mobile/Trading = spec-only v0.x | `README.md` | ⬜ |
| 4.2 | Ubah "Production-ready" → "opinionated security-first starter, v0.x" sampai Gelombang 3 selesai | `README.md`, `docs/PANDUAN-AWAM.md` | ⬜ |
| 4.3 | Hapus / haluskan klaim "Encrypted Mobile Storage", "SSL Pinning", "Trading Emergency Brake" di bagian "Security That's Already Built In" — saat ini **naratif tanpa kode**. Kembalikan setelah skeleton ada | `README.md:251-262` | ⬜ |
| 4.4 | Versi README yang lebih teknis untuk engineer (yang sekarang sangat "beginner-friendly" — bagus untuk onboarding, tapi audiens target "enterprise team" butuh signal teknis di atas) | `README.md` | ⬜ |

---

## 🧭 Aturan Kerja

1. **Satu gelombang dalam satu waktu.** Jangan mulai Gelombang 3 sebelum 1 & 2 selesai — janji mobile/trading tanpa fondasi = hutang teknis + marketing.
2. **Urut dalam gelombang.** 1.1 → 1.6 berurutan, masing-masing commit terpisah (`feat(skeleton): add rate limiting on auth endpoints`, dst.).
3. **Update kolom Status di file ini setiap item selesai**, lalu commit: `docs: update gap-analysis progress`. Commit kecil tidak apa-apa.
4. **Setiap endpoint/fitur baru wajib:** STRIDE singkat di `docs/adr/` + audit-log + test. Ini bukan opsional — `AGENTS.md` §3.3 & §5 sudah memerintahkan, jadi jangan tambahkan boilerplate, **ikuti saja**.
5. **Jangan tambah dependency baru bila stdlib cukup.** Rate limiter: Redis + pipeline manual, bukan `slowapi`. MFA: `pyotp` wajib (standar TOTP RFC 6238), itu pengecualian yang dapat diterima.
6. **Saat membuka repo ini di Cline/Cursor/Claude:** baca file ini pertama kali. AGENTS.md adalah kontrak, file ini adalah backlog-nya.
7. Repo lokal: `/home/tpam_su/Project/Baseline`. Sebelum mulai: `git pull --ff-only` (per 2026-09-21 lokal sudah di-sync ke v0.1.6).

---

## 📊 Konteks Pasar (sebagai pembanding)

- `mochrzlf/aegis-forge`: dibuat 2026-09-06, 5 stars, 0 forks, v0.1.6, 1 contributor.
- Kompetitor tidak langsung: `rizqinrr/viserys-agent` (workflow pack untuk AI coding agent — DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP, 29 skills, 7 personas, ~632-668 stars) menjual **disiplin proses**, bukan kode fondasi. Aegis Forge menjual **fondasi + keamanan**. Keduanya komplementer: forge project dulu, lalu masukkan Viserys agar agent bekerja konsisten.
- Belum ada validasi pihak ketiga. Wajar untuk umur 2 minggu — jangan klaim "production-ready" dulu.
