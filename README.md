# Enterprise Baseline

Template dan blueprint arsitektur untuk memulai proyek baru (Web, Mobile Android/iOS, atau EA Trading) dengan standar keamanan dan struktur yang sudah teruji.

[![DevSecOps CI Pipeline](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml/badge.svg)](https://github.com/mochrzlf/enterprise-baseline/actions/workflows/security.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Protected by Gitleaks](https://img.shields.io/badge/Protected%20by-Gitleaks-red.svg)](.gitleaks.toml)
[![Security Policy](https://img.shields.io/badge/Security-Policy-brightgreen.svg)](SECURITY.md)

---

## Latar Belakang

Setiap kali memulai proyek software baru, developer sering kali menghabiskan waktu berulang-ulang untuk:
- Menyiapkan otentikasi aman (rotasi refresh token, cookies HttpOnly).
- Menata skema database dan audit log yang tahan manipulasi.
- Memasang proteksi anti-bocor kredensial (pre-commit hook, gitleaks).
- Menentukan arsitektur folder agar kode tetap rapi saat proyek membesar.

Repositori ini dibuat untuk menyelesaikan masalah tersebut. Semua fondasi keamanan, dokumen spesifikasi (PRD & OpenAPI), template database PostgreSQL, dan alur kerja bantuan AI Agent (Hermes, Claude, Cursor) sudah siap pakai sejak hari pertama.

---

## Cakupan Proyek yang Didukung

Template ini menyediakan cetak biru teknis (*blueprints*) dan aturan untuk beberapa jenis kebutuhan:

- **Aplikasi Web & SaaS**: Session management dengan cookie `HttpOnly; Secure; SameSite=Strict`, proteksi CSRF/XSS, dan kontrak REST API OpenAPI 3.0.
- **Aplikasi Mobile (Android & iOS)**: Clean Architecture, penyimpanan token di hardware Keystore (`EncryptedSharedPreferences`), SSL Pinning, dan proteksi layar (`FLAG_SECURE`).
- **Sistem EA / Algorithmic Trading**: Manajemen risiko modal (*Hard Stop Loss* wajib, lot dinamis maksimal 1-2% risiko, dan *Emergency Circuit Breaker* jika drawdown harian menyentuh batas toleransi).
- **Backend & Database Core**: Role-Based Access Control (RBAC), alur persetujuan Maker-Checker, trigger audit log anti-manipulasi (*tamper-proof*), dan enkripsi kolom sensitif (AES-256-GCM).

---

## Cara Cepat Memulai (Quick Start)

Untuk membuat proyek baru dari template ini, jalankan perintah di terminal WSL/Linux:

```bash
# Clone repositori jika belum ada
git clone https://github.com/mochrzlf/enterprise-baseline.git
cd enterprise-baseline

# Buat proyek baru sesuai kebutuhan:
# 1. Untuk Web App:
make new NAME="PortalPasien" PATH="/home/tpam_su/Project/PortalPasien" TYPE="web"

# 2. Untuk Mobile App (Android/iOS):
make new NAME="MobileBanking" PATH="/home/tpam_su/Project/MobileBanking" TYPE="mobile"

# 3. Untuk EA Trading Bot:
make new NAME="GoldScalperEA" PATH="/home/tpam_su/Project/GoldScalperEA" TYPE="trading"

# 4. Untuk Proyek Fullstack:
make new NAME="CoreEnterprise" PATH="/home/tpam_su/Project/CoreEnterprise" TYPE="fullstack"
```

Skrip scaffolding akan otomatis:
1. Menyalin seluruh dokumen arsitektur, skrip, dan konfigurasi ke folder target.
2. Mengganti nama placeholder `[PROJECT_NAME]` menjadi nama proyek Anda.
3. Menjalankan `git init -b main`.
4. Memasang Git pre-commit hook yang terhubung ke Gitleaks agar file `.env` atau token tidak bisa ter-commit secara tidak sengaja.
5. Menyiapkan file `.env` lokal dari `.env.example`.

---

## Struktur Direktori

```
Baseline/
├── AGENTS.md                   # Kontrak kerja & batasan teknis saat dibantu AI Agent
├── README.md                   # Dokumentasi umum
├── SETUP.md                    # Panduan teknis inisialisasi & konfigurasi
├── SECURITY.md                 # Kebijakan pelaporan celah keamanan
├── LICENSE                     # Lisensi Apache-2.0
├── Makefile                    # Kumpulan perintah kerja cepat
├── .env.example                # Template variabel lingkungan
├── .gitattributes              # Penguncian format line-ending Unix (LF)
├── .editorconfig               # Standar indentasi & format editor
├── .gitleaks.toml              # Aturan audit rahasia & allowlist template
├── docker-compose.yml          # PostgreSQL 16, Redis 7, Mailpit, dan Prism Mock Server
├── docs/
│   ├── PRD-template.md         # Template kebutuhan produk tingkat tinggi
│   ├── PRD-detail-template.md  # Template user stories & acceptance criteria
│   ├── ui-design-template.md   # Panduan design system & UI tokens
│   ├── schema-template.sql     # Skema PostgreSQL (RBAC, triggers, audit log)
│   ├── openapi-template.yaml   # Kontrak REST API standar OpenAPI 3.0
│   ├── blueprints/             # Panduan arsitektur per domain (web, mobile, trading)
│   ├── security/               # Checklist keamanan mobile & kebijakan risiko trading
│   ├── diagrams/               # Diagram visual arsitektur & sequence (Mermaid)
│   └── adr/                    # Architecture Decision Records & analisis STRIDE
└── scripts/
    ├── init-new-project.sh     # Skrip pembuat proyek otomatis
    └── devsec-check.sh         # Skrip audit keamanan lokal & scan gitleaks
```

---

## Perintah Harian (Task Runner)

Repositori ini menyediakan `Makefile` untuk mempermudah eksekusi tanpa perlu menghafal path panjang:

- `make help` : Melihat daftar seluruh perintah yang tersedia.
- `make audit` : Menjalankan audit keamanan menyeluruh (cek file `.env`, private keys, dan scan Gitleaks).
- `make mock-api` : Menjalankan mock server API lokal di port 4010 dari `docs/openapi.yaml` (sangat berguna untuk developer mobile/frontend yang ingin mulai coding tanpa menunggu backend).
- `make up` : Menjalankan PostgreSQL, Redis, Mailpit, dan Prism via Docker Compose.
- `make down` : Mematikan seluruh kontainer Docker.
- `make hermes` : Membuka Hermes AI Agent langsung di terminal.
- `make hermes-ui` : Menjalankan Web Dashboard Hermes di browser (`http://127.0.0.1:9119`).

---

## Standar Keamanan Bawaan

- **Pre-Commit Shield:** Setiap kali Anda menjalankan `git commit`, hook otomatis memindai baris kode yang di-stage. Jika ada token API, private key, atau file `.env` yang masuk, commit langsung dibatalkan.
- **Four-Eyes Principle (Maker-Checker):** Transaksi penting memiliki constraint database di mana pembuat request tidak boleh menjadi penyetuju dirinya sendiri.
- **Audit Log Anti-Manipulasi:** Tabel `audit_logs` dilindungi trigger PostgreSQL yang menolak perintah `UPDATE` dan `DELETE`.
- **Enkripsi Data Sensitif:** Data pribadi disimpan dengan cipher AES-256-GCM (*Field-Level Encryption*).
- **Higiene API Trading:** Kunci API exchange atau broker diwajibkan hanya memiliki hak akses *Read* dan *Trade*, dengan hak akses penarikan dana (*Withdrawal*) dinonaktifkan secara permanen.
