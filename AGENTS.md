# AGENTS.md — Universal Project Baseline

> **PENTING UNTUK AI AGENT (Hermes / Claude / Cursor / LLM):**
> File ini dibaca secara otomatis pada setiap awal sesi development.
> Ini adalah **kontrak kerja permanen & single source of truth** untuk proyek ini.
> Baca seluruh dokumen ini sebelum membuat atau memodifikasi satu baris kode pun.

---

## 🎯 1. Filosofi Proyek & Referensi Standar

Setiap project yang diturunkan dari baseline ini WAJIB mengedepankan tiga pilar:
1. **Product-Driven:** Setiap baris kode harus mengacu pada spesifikasi di folder `docs/`.
2. **Secure-by-Design & IAM-First:** Menerapkan Zero Trust, Principle of Least Privilege (PoLP), dan Threat Modeling sebelum koding.
3. **Modern UI & High Polish:** Antarmuka responsif, bersih, tipografi terkurasi, dan berkarakter (bukan generic boilerplate).

### Dokumen Referensi Wajib:
| Dokumen | Deskripsi |
|---|---|
| `docs/PRD.md` | Ringkasan produk, problem statement, persona, metrik sukses |
| `docs/PRD-detail.md` | User Story & Acceptance Criteria (AC) per modul |
| `docs/ui-design.md` | Design System, color tokens, tipografi, dan mockup layar |
| `docs/openapi.yaml` | Kontrak API — WAJIB dipatuhi 100% |
| `docs/schema.sql` | Skema database PostgreSQL & integrity constraints |
| `docs/security-iam-policy.md` | Standar keamanan IAM, RBAC, dan kepatuhan UU PDP |
| `docs/security-access-matrix.md` | Security Access Matrix, Segregation of Duties (SoD), & Maker-Checker |
| `docs/adr/` | Architecture Decision Records & STRIDE Threat Modeling |

---

## 🏗️ 2. Standar Tech Stack

```
Frontend  : Next.js (App Router) / React + TypeScript + Tailwind CSS
UI Kit    : Radix UI / shadcn/ui primitives + Lucide Icons
Backend   : NestJS / FastAPI / Express + TypeScript / Python
ORM & DB  : Prisma / Drizzle ORM + PostgreSQL (v14+)
Caching   : Redis (Session, Rate Limiting, BullMQ)
Auth      : Google OAuth / OIDC + Short-lived JWT (15m) + HttpOnly Refresh Cookie
Validasi  : Zod / Pydantic (wajib di DTO/request boundary)
Security  : Helmet, CORS ketat, Argon2id/bcrypt, CSRF tokens
```

---

## ⚖️ 3. Aturan Keras (Non-Negotiable Rules)

### 3.1 Kontrak API & Format Response
Semua endpoint REST API HARUS mengembalikan response dengan struktur terstandarisasi:
```json
// SUKSES
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}

// ERROR
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED" | "FORBIDDEN" | "VALIDATION_ERROR" | "NOT_FOUND" | "INTERNAL_ERROR",
    "message": "Pesan ramah pengguna dalam Bahasa Indonesia",
    "details": {}
  }
}
```

### 3.2 Keamanan & IAM (Identity & Access Management)
1. **Token Transport Hygiene:**
   - DILARANG mengembalikan `refresh_token` di JSON body untuk disimpan di `localStorage`.
   - Refresh token WAJIB dikirim melalui `Set-Cookie` dengan flags:
     `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`.
   - Access token berumur maksimal 15 menit.
2. **Role-Based Access Control (RBAC) & Maker-Checker (Dual Control):**
   - Wajib mematuhi `docs/security-access-matrix.md`.
   - Aksi sensitif (role promotion, penarikan dana, perubahan limit) WAJIB menerapkan alur Maker-Checker (`approval_requests`). Maker DILARANG menjadi Checker sendiri.
   - Terapkan JML Kill-Switch: jika user `terminated` / `suspended`, seluruh token aktif wajib hangus seketika.
   - Setiap endpoint non-publik wajib memiliki Role Guard/Middleware (misal: `@Roles(['admin', 'member'])`).
3. **Pencegahan IDOR/BOLA:**
   - Setiap query pengambilan atau modifikasi resource wajib memeriksa kepemilikan pemilik:
     `WHERE id = :resourceId AND user_id = :currentUserId`.
4. **Step-Up Authentication:**
   - Aksi berisiko tinggi (ganti password, transfer saldo, penarikan dana, hapus akun) WAJIB meminta re-autentikasi atau challenge token.
5. **Audit Trail:**
   - Setiap mutasi data penting (auth, billing, privasi, perubahan role) WAJIB mencatat record ke tabel `audit_logs` (User ID, Action, IP Address, User Agent).

### 3.3 Automated Threat Modeling (STRIDE)
- Sebelum menulis kode untuk modul, endpoint, atau integrasi baru, AI Agent WAJIB melakukan analisis **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege).
- Dokumentasikan temuan ancaman dan strategi mitigasinya di `docs/adr/ADR-[NUM]-threat-model-[feature].md` sebelum koding.

### 3.4 Privasi Data (UU PDP) & Anti-Secret Leak
1. DILARANG mencatat PII (email, nomor telepon, plain nominal finansial) ke console log atau third-party analytics.
2. DILARANG meng-commit file `.env` atau API secret key dalam bentuk apapun.
3. Kredensial OAuth atau secret pihak ketiga yang disimpan di database WAJIB dienkripsi menggunakan **AES-256-GCM (Field-Level Encryption)**.

### 3.5 Standar Diagram Desain Arsitektur
- Untuk visualisasi arsitektur, sequence auth, data flow, dan skema database, gunakan skill \diagram-design\ yang menghasilkan file HTML/SVG editorial standalone di folder \docs/diagrams/\.

### 3.6 Standar UI/UX
1. Ikuti `docs/ui-design.md` secara konsisten: Card radius 16px, button radius 12px, shadow lembut (`0 1px 3px rgba(0,0,0,0.06)`), padding lapang.
2. Font Display/Angka: **Plus Jakarta Sans**; Font Body: **Inter**.
3. Gunakan warna fungsional secara konsisten (Hijau = success/income, Merah = danger/expense, dsb).
4. Responsif Mobile-first.

---

## 🧪 4. Standar Pengujian (Testing Requirements)

Setiap implementasi fitur baru minimal wajib memiliki:
1. **Unit Test (Happy Path):** Memastikan logika bisnis berjalan sesuai ekspektasi.
2. **Unit Test (Validation & Boundary):** Menguji input invalid, boundary numbers, dan missing fields.
3. **Security Test:**
   - Menguji akses tanpa autentikasi (harus 401 Unauthorized).
   - Menguji akses dengan role tidak sesuai (harus 403 Forbidden).
   - Menguji akses ke resource milik user lain / IDOR probe (harus 403 atau 404).

---

## 📋 5. Panduan Workflow AI Agent

Ketika user memberikan tugas:
1. **Pahami:** Periksa apakah modul tersebut sudah ada di `docs/PRD-detail.md` atau `docs/openapi.yaml`.
2. **Threat Model:** Analisis potensi risiko keamanan (STRIDE) dan tentukan mitigasinya.
3. **Implementasi:** Tulis kode yang clean, modular, dan terstruktur.
4. **Verifikasi:** Jalankan unit test, security test, dan linter sebelum melaporkan bahwa pekerjaan selesai.
