# Enterprise Baseline Project Template
### Production-Grade Fullstack & Security Blueprint

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)
[![Compliance](https://img.shields.io/badge/Compliance-UU%20PDP%202022-emerald.svg)](docs/security-iam-policy.md)

Baseline ini adalah fondasi standar emas (*gold-standard baseline*) untuk membangun aplikasi web modern yang aman, terstruktur rapi, dan siap skala enterprise. 

Dirancang khusus untuk dioperasikan bersama **AI Coding Agents (Hermes Agent, Claude, Cursor)** dengan filosofi **Secure-by-Design**, **IAM-First**, dan **Modern UI System**.

---

## 🌟 Pilar Utama Baseline

1. **Identity & Access Management (IAM) Rigor:**
   - Standar Session & Token RFC 6749 (Refresh Token Rotation).
   - Penyimpanan token aman via `HttpOnly; Secure; SameSite=Strict` Cookie.
   - Enforce RBAC/ABAC di level middleware dan database.
   - Segregation of Duties (Maker-Checker / Four-Eyes Principle) pada transaksi kritis.
   - Audit Logging terstruktur dan tamper-proof (anti-manipulasi) untuk setiap mutasi data sensitif.

2. **Automated Threat Modeling (STRIDE):**
   - Setiap fitur baru wajib melalui evaluasi ancaman STRIDE sebelum koding, tercatat rapi di `docs/adr/`.

3. **Modern UI/UX Design System:**
   - Typography stack terkurasi (*Plus Jakarta Sans* + *Inter*).
   - Mobile-first responsive, 16px soft radius cards, subtle shadows, dan palet warna berkarakter.

4. **Kepatuhan Privasi (UU PDP Indonesia No. 27/2022):**
   - Consent management, data minimization (anti-PII logging), right to erasure (*Right to be Forgotten*), dan Field-Level Encryption (AES-256-GCM).

---

## 📁 Struktur Direktori

```
Baseline/
├── AGENTS.md                   # Kontrak kerja & aturan keras untuk AI Agent
├── README.md                   # Dokumentasi umum baseline
├── SETUP.md                    # Panduan inisialisasi project baru
├── SECURITY.md                 # Kebijakan pelaporan kerentanan (Vulnerability Disclosure)
├── LICENSE                     # Lisensi resmi Apache-2.0
├── Makefile                    # Task runner terpadu (make audit, up, down, dll)
├── .env.example                # Template variabel lingkungan ter-hardening
├── .gitattributes              # Menegakkan Linux line endings (LF) lintas OS
├── .editorconfig               # Konsistensi formatting editor & IDE
├── .gitleaks.toml              # Konfigurasi audit rahasia & allowlist
├── docker-compose.yml          # PostgreSQL 16, Redis 7, & Mailpit
├── docs/
│   ├── PRD-template.md         # Template PRD tingkat tinggi (Bisnis & Fitur)
│   ├── PRD-detail-template.md  # Template spesifikasi User Stories & AC
│   ├── ui-design-template.md   # Panduan Design System & UI Tokens
│   ├── schema-template.sql     # Skema PostgreSQL dengan RBAC & Audit Log
│   ├── openapi-template.yaml   # Kontrak REST API standar OpenAPI 3.0
│   ├── security-iam-policy.md  # Doktrin lengkap IAM & AppSec Policy
│   └── adr/
│       ├── ADR-000-template.md # Template Architecture Decision Record + STRIDE
│       └── ADR-001-Threat-Modeling-Standard.md
└── scripts/
    ├── init-new-project.sh     # Script otomatis scaffolding project baru
    └── devsec-check.sh         # Script automated security audit & secret scan
```

---

## ⚡ Task Runner (Makefile)

Baseline menyertakan `Makefile` untuk menyederhanakan operasional harian:

| Perintah | Deskripsi |
| :--- | :--- |
| `make help` | Menampilkan seluruh daftar perintah yang tersedia |
| `make audit` | Menjalankan audit keamanan menyeluruh (Git, .env, Private Key, Gitleaks) |
| `make audit-staged` | Menjalankan audit khusus file yang sedang di-stage (mode pre-commit) |
| `make up` | Menjalankan stack database & messaging lokal (`docker compose up -d`) |
| `make down` | Menghentikan stack lokal (`docker compose down`) |
| `make status` | Memeriksa status kontainer Docker |
| `make hermes` | Membuka Hermes AI Agent di CLI terminal |
| `make hermes-ui` | Menjalankan Hermes Web Dashboard di latar belakang (`http://127.0.0.1:9119`) |
| `make new NAME=... PATH=...` | Membuat proyek baru dari baseline |

---

## 🚀 Cara Menggunakan Baseline Ini

Untuk membuat project baru berbasis template ini, cukup jalankan:

```bash
cd /home/tpam_su/Project/Baseline
make new NAME="NamaProjectBaru" PATH="/home/tpam_su/Project/NamaProjectBaru"

# Atau menggunakan shortcut terminal
new-project "NamaProjectBaru" "/home/tpam_su/Project/NamaProjectBaru"
```

Lalu buka Hermes Agent di terminal Anda:
```bash
~/.local/bin/hermes
```
Dan perintahkan:
> *"Hermes, tolong baca AGENTS.md dan isi docs/PRD.md untuk project baru ini sesuai deskripsi berikut..."*
