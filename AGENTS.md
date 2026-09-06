# AGENTS.md — Universal Multi-Domain Enterprise Baseline

> **PENTING UNTUK AI AGENT (Hermes / Claude / Cursor / LLM) & DEVELOPER:**
> File ini dibaca secara otomatis pada setiap awal sesi development.
> Ini adalah **kontrak kerja permanen & single source of truth** untuk seluruh proyek turunan:
> - 🌐 **Web Applications & SaaS Platforms**
> - 📱 **Mobile Applications (Android & iOS)**
> - 📈 **Algorithmic & EA Trading Systems**
> - 🏢 **Enterprise Backend Services & Data Infrastructure**
> 
> Baca seluruh dokumen ini sebelum membuat atau memodifikasi satu baris kode pun.

---

## 🎯 1. Filosofi Proyek & Referensi Standar

Setiap project yang diturunkan dari baseline ini WAJIB mengedepankan empat pilar universal:
1. **Product-Driven & Specification-First:** Setiap baris kode harus mengacu pada spesifikasi di folder `docs/` (PRD, OpenAPI, UI tokens, atau Trading Strategy Sheet).
2. **Secure-by-Design & Zero Trust:** Menerapkan Zero Trust, Principle of Least Privilege (PoLP), Threat Modeling (STRIDE), dan perlindungan rahasia otomatis.
3. **Rigid Risk Management:** Khusus sistem finansial/trading, proteksi modal (*Capital Preservation*) dan batas risiko drawdown adalah prioritas absolut di atas perolehan profit.
4. **High Polish & Observability:** Antarmuka responsif dan aksesibel, logging terstruktur anti-PII, serta jejak audit yang kekal (*tamper-proof*).

### Dokumen Referensi Wajib:
| Dokumen | Deskripsi |
|---|---|
| `docs/PRD.md` | Ringkasan produk, problem statement, persona, metrik sukses |
| `docs/PRD-detail.md` | User Story & Acceptance Criteria (AC) per modul |
| `docs/ui-design.md` | Design System, color tokens, tipografi, dan mockup layar |
| `docs/openapi.yaml` | Kontrak REST API — WAJIB dipatuhi 100% |
| `docs/schema.sql` | Skema database PostgreSQL & integrity constraints |
| `docs/security-iam-policy.md` | Standar keamanan IAM, RBAC, dan kepatuhan UU PDP |
| `docs/security-access-matrix.md` | Matriks Entitlement, Segregation of Duties (SoD), & Maker-Checker |
| `docs/blueprints/` | Cetak biru arsitektur khusus per domain (Web, Mobile, EA Trading) |
| `docs/security/` | Checklist keamanan khusus (Mobile AppSec, Trading Risk Policy) |
| `docs/diagrams/` | Diagram visual arsitektur, sequence autentikasi, dan flow eksekusi |
| `docs/adr/` | Architecture Decision Records & STRIDE Threat Modeling |

---

## 🏗️ 2. Standar Tech Stack per Domain

AI Agent wajib mengadopsi stack terstandarisasi berikut sesuai jenis proyek:

```
[Web Applications]
Frontend  : Next.js (App Router) / React / Vue + TypeScript + Tailwind CSS
UI Kit    : Radix UI / shadcn/ui primitives + Lucide Icons
Backend   : NestJS / FastAPI / Express + TypeScript / Python

[Mobile Applications]
Android   : Kotlin (Jetpack Compose) / Clean Architecture + Coroutines / Flow
Cross-Plat: Flutter (Dart) / React Native (TypeScript)
Security  : Android Keystore, EncryptedSharedPreferences, SSL Pinning, FLAG_SECURE

[EA & Quantitative Trading Systems]
MetaTrader: MQL5 / MQL4 (Expert Advisors, Custom Indicators, Scripts)
Python    : Python 3.11+ (ccxt, pandas, numpy, backtrader / vectorbt, MetaAPI)
Protocols : FIX Protocol (4.4/5.0), WebSocket low-latency, REST API
Messaging : Redis Streams / BullMQ untuk antrean order dan streaming tick

[Core Infrastructure & Shared Services]
Database  : PostgreSQL 16+ (RBAC, Triggers, Kill-Switch, AES-256 FLE)
Caching   : Redis 7+ (Session Store, Rate Limiter, Market Data Cache)
Testing   : Vitest / Jest / PyTest / JUnit5 / MT5 Strategy Tester
Mocking   : Stoplight Prism (Mock API Server di port 4010)
DevSecOps : Gitleaks, Semgrep SAST, Trivy, Git Pre-Commit Hooks
```

---

## ⚖️ 3. Aturan Keras Universal (Core Non-Negotiable Rules)

### 3.1 Kontrak API & Format Response
Semua endpoint REST API HARUS mengembalikan format terstandarisasi:
```json
// SUKSES
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "per_page": 20, "total": 100 }
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

### 3.2 Keamanan IAM & Privileged Access
1. **Role-Based Access Control (RBAC) & Maker-Checker:**
   - Aksi kritis (role promotion, penarikan dana, perubahan limit, eksekusi parameter trading) WAJIB menerapkan prinsip Four-Eyes (`maker_user_id <> checker_user_id`).
   - JML Kill-Switch: Perubahan status pengguna menjadi `terminated`/`suspended` wajib mencabut seluruh token dan sesi aktif seketika.
2. **Pencegahan IDOR / BOLA:**
   - Setiap query modifikasi data wajib memverifikasi kepemilikan: `WHERE id = :id AND user_id = :currentUserId`.
3. **Immutable Audit Trail:**
   - Seluruh mutasi data dicatat ke tabel `audit_logs` yang dilindungi trigger anti-tamper (larangan keras `UPDATE` dan `DELETE`).
4. **Privasi Data (UU PDP) & Anti-Secret Leak:**
   - DILARANG mencatat data pribadi (PII), password, nomor kartu, atau saldo ke console log.
   - DILARANG meng-commit file `.env`, keystore `.jks`, atau secret token ke Git.

### 3.3 Automated Threat Modeling (STRIDE)
- Sebelum menulis kode modul, endpoint, atau strategi baru, wajib menyusun analisis **STRIDE** (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) di folder `docs/adr/`.

---

## 🚀 4. Modul Mesin Eksekusi Khusus Domain

### 4.1 🌐 Web Application Engine
1. **Cookie Transport Security:** Refresh token WAJIB dikirim via `Set-Cookie` dengan atribut: `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`. Dilarang mengembalikan refresh token di response JSON body untuk disimpan di `localStorage`.
2. **Security Headers:** Terapkan Helmet.js (CSP ketat, HSTS, X-Frame-Options: DENY, X-Content-Type-Options: nosniff).
3. **Core Web Vitals:** Pastikan rendering komponen responsif, optimasi gambar (WebP/AVIF), dan LCP < 2.5s.

### 4.2 📱 Mobile Application Engine (Android & iOS)
1. **Hardware Keystore Storage:**
   - ❌ DILARANG keras menyimpan token, kata sandi, atau data biometrik di plain `SharedPreferences` / `NSUserDefaults`.
   - ✅ WAJIB menggunakan **Android Keystore System** + `EncryptedSharedPreferences` (atau `flutter_secure_storage` / `react-native-keychain`).
2. **SSL / Certificate Pinning:**
   - Wajib menyertakan konfigurasi `network_security_config.xml` untuk mengunci hash sertifikat SSL publik server backend demi mencegah serangan Man-in-the-Middle (MitM).
3. **Screen Protection (`FLAG_SECURE`):**
   - Layar yang memuat data finansial, OTP, saldo, atau identitas wajib diproteksi dengan `FLAG_SECURE` untuk memblokir screenshot dan screen-recorder.
4. **Anti-Tampering & Minifikasi:**
   - Wajib mengaktifkan **R8 / ProGuard** untuk meminifikasi dan mengaburkan (*obfuscate*) kode produksi.

### 4.3 📈 Algorithmic & EA Trading Engine
1. **Doktrin Proteksi Modal (Capital Preservation First):**
   - ❌ DILARANG KERAS mengeksekusi order trading tanpa **Hard Stop Loss (SL)** yang terhitung matematis.
   - ❌ DILARANG menggunakan strategi martingal murni (pelipatgandaan lot tanpa batas) yang berpotensi *Margin Call / Account Wipeout*.
2. **Kalkulasi Lot Dinamis (Dynamic Position Sizing):**
   - Ukuran lot WAJIB dihitung secara dinamis berdasarkan persentase risiko modal per transaksi (maksimal **1% s.d. 2% dari Equity**), memperhitungkan jarak Stop Loss dan nilai tick/pip instrumen.
3. **Emergency Circuit Breaker (Max Daily Drawdown Kill-Switch):**
   - EA wajib memonitor floating drawdown harian secara berkala.
   - Jika *Daily Drawdown* mencapai batas toleransi (misal **5% Equity**), sistem wajib:
     1. Menutup seluruh posisi terbuka (*Emergency Close All*).
     2. Membatalkan semua pending order.
     3. Mengaktifkan *trading pause* otomatis hingga pergantian hari pasar.
     4. Mengirimkan notifikasi darurat (Telegram / Discord / Email).
4. **Higiene Hak Akses Kunci API (API Key Permission Segregation):**
   - Kunci API exchange (misal Binance, Bybit, IBKR) HANYA boleh memiliki izin **Read Info** dan **Spot/Futures Trading**.
   - ❌ **DILARANG KERAS MENGAKTIFKAN PERMISSION WITHDRAWAL** pada API key yang digunakan oleh EA/Algoritma.
5. **Toleransi Slippage & Spread Filter:**
   - EA wajib memvalidasi spread sebelum eksekusi. Batalkan order jika spread melebar melebihi batas wajar (misal saat rilis berita NFP, CPI, FOMC).
6. **Siklus Pengujian Wajib (Anti-Overfitting SOP):**
   - Sebelum rilis ke akun riil, algoritma wajib melalui 5 gerbang:
     `In-Sample Backtest (70% data) -> Out-of-Sample Test (30% data) -> Walk-Forward Analysis -> Demo / Paper Trading (Min. 30 hari) -> Akun Live Berisiko Rendah (Cent/Micro)`.

---

## 🧪 5. Standar Pengujian (Testing Requirements)

Setiap implementasi fitur baru wajib melewati rangkaian pengujian:
1. **Unit Test (Logika Bisnis):** Memvalidasi kalkulasi nominal, alur otorisasi, dan state transitions.
2. **Boundary & Negative Test:** Input invalid, angka minus, overflow nominal, missing headers.
3. **Security Test:**
   - Akses tanpa token (harus 401 Unauthorized).
   - Akses dengan role tidak berhak (harus 403 Forbidden).
   - IDOR Probe terhadap user lain (harus 403 atau 404).
4. **Domain-Specific Tests:**
   - Mobile: Pengujian offline caching dan token expiry refresh flow.
   - Trading: Pengujian simulasi slippage ekstrem, margin call scenario, dan circuit breaker trigger.

---

## 📋 6. Panduan Alur Kerja AI Agent (Execution Workflow)

Ketika user memberikan tugas:
1. **Identifikasi Domain:** Tentukan domain proyek (`Web`, `Mobile`, `EA Trading`, atau `Fullstack`).
2. **Konsultasi Blueprint:** Rujuk berkas arsitektur di `docs/blueprints/` yang relevan.
3. **Evaluasi Ancaman & Risiko:** Lakukan analisis STRIDE (untuk aplikasi) atau *Risk Breakdown* (untuk trading EA) di `docs/adr/`.
4. **Visualisasi Diagram:** Buat atau perbarui diagram visual di `docs/diagrams/` sebelum menulis kode kompleks.
5. **Implementasi Kode:** Tulis kode yang clean, terisolasi dalam arsitektur berlapis (*Clean Architecture*), dan teruji.
6. **Verifikasi Keamanan:** Jalankan `make audit` dan unit test sebelum melaporkan bahwa pekerjaan selesai.
