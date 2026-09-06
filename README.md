# Universal Enterprise Baseline Blueprint
### Gold-Standard Framework for Web, Mobile, EA Trading, & Enterprise Systems

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)
[![Compliance](https://img.shields.io/badge/Compliance-UU%20PDP%202022-emerald.svg)](docs/security-iam-policy.md)

Baseline ini adalah fondasi standar emas (*universal enterprise blueprint*) yang dirancang khusus untuk membangun solusi perangkat lunak skala produksi, siap diaudit, dan berstandar institusi.

Dapat dioperasikan secara otonom bersama **AI Coding Agents (Hermes Agent, Claude, Cursor)** maupun oleh tim rekayasa perangkat lunak manusia dengan dukungan penuh untuk 4 domain:
1. 🌐 **Web Applications & SaaS:** Fullstack, modern UI system, SSR/CSR, cookie session RFC 6749, anti-XSS/CSP.
2. 📱 **Mobile Applications (Android & iOS):** Jetpack Compose / Flutter, hardware-backed Keystore, SSL/Certificate Pinning, `FLAG_SECURE`, dan proteksi R8/ProGuard.
3. 📈 **Algorithmic & EA Trading Systems:** Expert Advisor (MQL5/Python), doktrin *Capital Preservation*, kalkulasi lot dinamis, *Emergency Circuit Breaker*, dan *Anti-Overfitting SOP*.
4. 🏢 **Enterprise Backend & IAM Core:** RBAC/ABAC, *Maker-Checker (Four-Eyes Principle)*, *JML Kill-Switch*, enkripsi tingkat kolom (AES-256-GCM), dan *Immutable Audit Trail*.

---

## 🌟 Pilar Utama Baseline

1. **Specification-First & AI-Agent Operating Contract:**
   - Kontrak kerja permanen di `AGENTS.md` mengatur aturan keras (*non-negotiable rules*) sebelum AI menulis baris kode pertama.
2. **Rigid Identity & Access Management (IAM):**
   - Refresh Token Rotation (RFC 6749) dengan transport cookie `HttpOnly; Secure; SameSite=Strict`.
   - Integritas *Maker-Checker* ditegakkan di level database constraint (`maker_user_id <> checker_user_id`).
   - Jejak audit anti-manipulasi (*tamper-proof audit trail*).
3. **Institutional Risk Management (EA Trading):**
   - Kewajiban *Hard Stop Loss* di setiap order, larangan martingal murni, dan pemutus sirkuit otomatis jika terjadi *Maximum Daily Drawdown* (>5%).
4. **Mobile AppSec Rigor:**
   - Penyimpanan kredensial terisolasi di hardware Keystore, anti-sniffing via Certificate Pinning, dan pencegahan perekaman layar sensitif.
5. **Automated DevSecOps:**
   - Git pre-commit hook cerdas memblokir file `.env`, private key, dan secret token via Gitleaks secara real-time.

---

## 📁 Struktur Direktori Repositori

```
Baseline/
├── AGENTS.md                   # Kontrak kerja & aturan keras untuk AI Agent & Devs
├── README.md                   # Dokumentasi umum baseline
├── SETUP.md                    # Panduan inisialisasi dan alur kerja harian
├── SECURITY.md                 # Kebijakan pelaporan kerentanan (Vulnerability Disclosure)
├── LICENSE                     # Lisensi resmi Apache-2.0
├── Makefile                    # Task runner terpadu (audit, mock-api, up, down, dll)
├── .env.example                # Template variabel lingkungan ter-hardening
├── .gitattributes              # Menegakkan Linux line endings (LF) lintas OS
├── .editorconfig               # Konsistensi formatting editor & IDE
├── .gitleaks.toml              # Konfigurasi audit rahasia, custom rules & allowlist
├── docker-compose.yml          # PostgreSQL 16, Redis 7, Mailpit, & Prism Mock Server
├── docs/
│   ├── PRD-template.md         # Template PRD tingkat tinggi (Bisnis & Fitur)
│   ├── PRD-detail-template.md  # Template spesifikasi User Stories & AC
│   ├── ui-design-template.md   # Panduan Design System & UI Tokens
│   ├── schema-template.sql     # Skema PostgreSQL dengan RBAC & Audit Log
│   ├── openapi-template.yaml   # Kontrak REST API standar OpenAPI 3.0
│   ├── security-iam-policy.md  # Doktrin lengkap IAM & AppSec Policy
│   ├── security-access-matrix.md # Matriks Entitlement & Segregation of Duties
│   ├── blueprints/             # Cetak biru arsitektur khusus per domain
│   │   ├── web-application-blueprint.md
│   │   ├── mobile-application-blueprint.md
│   │   └── ea-trading-blueprint.md
│   ├── security/               # Kebijakan & checklist keamanan lanjutan
│   │   ├── mobile-security-checklist.md
│   │   └── trading-risk-policy.md
│   ├── diagrams/               # Diagram visual arsitektur & sequence (Mermaid)
│   │   ├── system-architecture-universal.md
│   │   ├── mobile-auth-sequence.md
│   │   └── ea-trading-execution-flow.md
│   └── adr/
│       ├── ADR-000-template.md # Template Architecture Decision Record + STRIDE
│       └── ADR-001-Threat-Modeling-Standard.md
└── scripts/
    ├── init-new-project.sh     # Script otomatis scaffolding multi-domain
    └── devsec-check.sh         # Script automated security audit & secret scan
```

---

## ⚡ Task Runner (Makefile)

Baseline menyertakan `Makefile` untuk standardisasi operasional harian:

| Perintah | Deskripsi |
| :--- | :--- |
| `make help` | Menampilkan seluruh daftar perintah yang tersedia |
| `make audit` | Menjalankan audit keamanan menyeluruh (Git, .env, Private Key, Gitleaks) |
| `make audit-staged` | Menjalankan audit khusus file yang sedang di-stage (mode pre-commit) |
| `make mock-api` | Menjalankan Prism Mock API Server (`http://localhost:4010`) |
| `make up` | Menjalankan stack lokal (Postgres, Redis, Mailpit, Prism) |
| `make down` | Menghentikan seluruh stack Docker Compose |
| `make status` | Memeriksa status kontainer Docker |
| `make hermes` | Membuka Hermes AI Agent di CLI terminal |
| `make hermes-ui` | Menjalankan Hermes Web Dashboard di port 9119 |
| `make new NAME=... PATH=... TYPE=...` | Membuat proyek baru dari baseline |

---

## 🚀 Cara Membuat Proyek Baru Berdasarkan Domain

Gunakan perintah `make new` atau script `init-new-project.sh` dengan menentukan tipe domain:

### 1. Proyek Web Application / SaaS
```bash
make new NAME="PortalKesehatan" PATH="/home/tpam_su/Project/PortalKesehatan" TYPE="web"
```

### 2. Proyek Mobile Application (Android / iOS)
```bash
make new NAME="MobileBanking" PATH="/home/tpam_su/Project/MobileBanking" TYPE="mobile"
```
*(Tip: Jalankan `make mock-api` di folder proyek untuk langsung menguji API di emulator).*

### 3. Proyek EA / Algorithmic Trading
```bash
make new NAME="GoldScalperEA" PATH="/home/tpam_su/Project/GoldScalperEA" TYPE="trading"
```
*(Tip: Seluruh aturan manajemen risiko dan circuit breaker langsung aktif di `docs/security/trading-risk-policy.md`).*

### 4. Proyek Fullstack Enterprise
```bash
make new NAME="EnterpriseCore" PATH="/home/tpam_su/Project/EnterpriseCore" TYPE="fullstack"
```
