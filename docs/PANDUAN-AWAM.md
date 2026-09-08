# 📘 PANDUAN LENGKAP AEGIS-FORGE UNTUK ORANG AWAM

> **Dokumen ini ditulis untuk Anda yang BUKAN programmer** — dijelaskan dengan bahasa sehari-hari, tanpa jargon teknis yang membingungkan. Jika Anda bisa menggunakan WhatsApp dan Microsoft Word, Anda bisa memahami panduan ini.

---

## 📑 Daftar Isi

1. [Apa Itu Aegis-Forge? (Penjelasan Sederhana)](#1-apa-itu-aegis-forge)
2. [Kenapa Aegis-Forge Ada? Masalah yang Dipecahkan](#2-kenapa-aegis-forge-ada)
3. [Istilah-Istilah Penting (Kamus Awam)](#3-kamus-istilah-awam)
4. [Apa Saja yang Bisa Dibuat dengan Aegis-Forge?](#4-apa-yang-bisa-dibuat)
5. [Struktur Folder: Peta Jalan Proyek](#5-struktur-folder)
6. [Keamanan yang Sudah Terpasang Otomatis](#6-keamanan-bawaan)
7. [Tutorial: Cara Membuat Proyek Baru (Langkah demi Langkah)](#7-tutorial-membuat-proyek)
8. [Cara Kerja dengan AI (Claude, Cursor, dll)](#8-cara-kerja-dengan-ai)
9. [Perintah-Perintah Penting (Cheat Sheet)](#9-perintah-penting)
10. [Studi Kasus: Contoh Proyek Nyata](#10-studi-kasus)
11. [Pertanyaan yang Sering Ditanyakan (FAQ)](#11-faq)
12. [Troubleshooting: Masalah Umum & Solusinya](#12-troubleshooting)

---

## 1. Apa Itu Aegis-Forge?

### 🏠 Analogi Sederhana: Rumah Contoh

Bayangkan Anda ingin membangun **rumah**. Ada dua cara:

| Cara Lama (Tanpa Aegis-Forge) | Cara Baru (Dengan Aegis-Forge) |
|---|---|
| Beli tanah kosong | Beli **rumah contoh yang fondasinya sudah kokoh** |
| Gali fondasi sendiri | Fondasi sudah jadi |
| Pasang pipa air sendiri | Pipa & listrik sudah terpasang |
| Pasang alarm keamanan sendiri | Alarm sudah aktif |
| **Bulan 1:** baru mulai bangun tembok | **Hari 1:** tinggal pilih cat & perabot |

**Aegis-Forge adalah "rumah contoh" untuk software.** Ia bukan aplikasi jadi — ia adalah **fondasi lengkap** yang sudah mencakup:
- 🔐 **Keamanan** — supaya password & data pengguna tidak bocor
- 📋 **Panduan langkah-demi-langkah** — untuk Anda dan untuk AI
- ✅ **Checklist kualitas** — supaya tidak ada yang terlewat sebelum rilis
- 🤖 **"Pagar pengaman" untuk AI** — aturan agar AI yang menulis kode tidak membuat kesalahan berbahaya

### 🎯 Definisi Resmi (Versi Sederhana)

> **Aegis-Forge = template (cetakan) siap pakai untuk membangun aplikasi Web, aplikasi Mobile (Android/iPhone), dan Robot Trading — dengan keamanan tingkat perusahaan besar, tanpa perlu mengatur semuanya dari nol.**

### 💡 Poin Penting untuk Dipahami

- Aegis-Forge **BUKAN aplikasi jadi** — ia adalah **titik awal** (starting point)
- Aegis-Forge **GRATIS** — lisensi Apache-2.0, boleh dipakai untuk pribadi maupun komersial
- Aegis-Forge **dirancang untuk bekerja dengan AI** — Anda cukup menjelaskan apa yang Anda mau, AI yang menulis kodenya, Aegis-Forge memastikan hasilnya aman

---

## 2. Kenapa Aegis-Forge Ada?

### 😩 Masalah yang Sering Terjadi

Setiap kali seseorang memulai proyek software, mereka menghabiskan **hari-hari pertama** menyelesaikan masalah yang **sama persis**, berulang-ulang:

1. **"Bagaimana cara membuat sistem login yang aman?"**
   - Password harus di-enkripsi, sesi harus kedaluwarsa, dll.

2. **"Bagaimana cara mencatat siapa melakukan apa?"** (audit trail)
   - Penting untuk investigasi jika ada masalah

3. **"Bagaimana cara mencegah API key bocor ke internet?"**
   - Satu kesalahan kecil = data dicuri

4. **"Bagaimana cara mengatur folder supaya kode tidak berantakan?"**
   - Proyek kecil jadi besar, kode jadi sulit dicari

### ✅ Solusi Aegis-Forge

Aegis-Forge menyelesaikan **semua masalah di atas SEBELUM Anda mulai**. Semua pola arsitektur inti, checklist keamanan, dan aturan AI sudah siap **sejak hari pertama**.

---

## 3. Kamus Istilah Awam

Sebelum lanjut, pahami dulu istilah-istilah ini. Saya jelaskan dengan analogi sehari-hari.

### 📦 Istilah Dasar

| Istilah | Arti Sebenarnya | Analogi Sederhana |
|---|---|---|
| **Template / Baseline** | Cetakan dasar yang bisa disalin | Seperti **fotokopi formulir kosong** — Anda tinggal isi |
| **Repository (repo)** | Tempat menyimpan semua file proyek | Seperti **map/binder** berisi semua dokumen proyek |
| **Clone** | Menyalin repo dari internet ke komputer Anda | Seperti **mengunduh** semua file ke laptop |
| **Commit** | Menyimpan perubahan (dengan catatan apa yang berubah) | Seperti **"Save" + tulis tanggal & keterangan** |
| **Framework** | "Mesin" yang menjalankan aplikasi | Seperti **mesin mobil** — Aegis-Forge adalah "bodi + aturan berkendaranya" |

### 🔐 Istilah Keamanan

| Istilah | Arti Sebenarnya | Analogi Sederhana |
|---|---|---|
| **API Key** | Kunci rahasia untuk mengakses layanan pihak ketiga | Seperti **kunci rumah** — jangan sampai jatuh ke tangan orang lain |
| **Enkripsi** | Mengacak data supaya tidak bisa dibaca tanpa kunci | Seperti **menulis surat dengan kode rahasia** |
| **Audit Trail** | Catatan siapa melakukan apa, kapan | Seperti **CCTV + buku tamu** yang tidak bisa dihapus |
| **RBAC** | Aturan siapa boleh akses apa (berdasarkan peran) | Seperti **kartu akses kantor** — manajer bisa buka ruang server, staf tidak |
| **Secrets** | Data rahasia (password, API key, dll) | Seperti **PIN ATM** — jangan pernah ditulis di tempat yang bisa dilihat orang |

### 🤖 Istilah AI & Pengembangan

| Istilah | Arti Sebenarnya | Analogi Sederhana |
|---|---|---|
| **AI Agent** | AI yang bisa menulis kode (Claude, Cursor, dll) | Seperti **asisten pribadi** yang bisa mengetik untuk Anda |
| **PRD** | Dokumen "apa yang mau dibuat" | Seperti **denah rumah** sebelum dibangun |
| **OpenAPI** | Kontrak "bagaimana aplikasi berkomunikasi" | Seperti **menu restoran** — daftar apa saja yang bisa dipesan |
| **Schema (Database)** | Struktur tabel untuk menyimpan data | Seperti **lemari arsip** — di mana kertas apa disimpan |
| **Blueprint** | Panduan arsitektur per jenis proyek | Seperti **resep masakan** per jenis hidangan |
| **CI/CD** | Otomatis mengecek & mengetes kode setiap ada perubahan | Seperti **quality control di pabrik** — setiap produk dicek sebelum keluar |

### 💻 Istilah Teknis Ringan

| Istilah | Arti Sebenarnya | Analogi Sederhana |
|---|---|---|
| **Docker** | Menjalankan aplikasi dalam "kotak" terisolasi | Seperti **container/kontainer** — semua yang dibutuhkan sudah di dalam |
| **PostgreSQL** | Database (tempat menyimpan data) | Seperti **gudang data** yang terorganisir |
| **Redis** | Penyimpanan sementara yang super cepat | Seperti **meja kerja** — barang yang sering dipakai diletakkan di atas, bukan di gudang |
| **Git** | Sistem untuk melacak perubahan file | Seperti **"Track Changes" di Word**, tapi untuk seluruh proyek |
| **Makefile** | Kumpulan perintah singkat (shortcut) | Seperti **tombol speed dial** — tekan 1 tombol, jalankan tugas panjang |

---

## 4. Apa yang Bisa Dibuat?

Aegis-Forge mendukung **4 jenis proyek utama**:

### 🌐 A. Aplikasi Web & SaaS

**Contoh:** Sistem informasi klinik, portal pelanggan, dashboard bisnis, toko online

**Yang sudah disiapkan:**
- Login aman (password terenkripsi, sesi otomatis kedaluwarsa)
- Perlindungan dari serangan umum (XSS, CSRF — hacker tidak bisa menyisipkan kode jahat)
- "Kontrak API" yang jelas (frontend & backend tidak salah paham)

### 📱 B. Aplikasi Mobile (Android & iPhone)

**Contoh:** E-wallet, aplikasi absensi, aplikasi kesehatan

**Yang sudah disiapkan:**
- Penyimpanan data sensitif di **brankas perangkat** (Android Keystore) — bukan di file biasa
- Koneksi aman (SSL Pinning — mencegah penyadapan)
- Layar anti-screenshot untuk data sensitif (FLAG_SECURE)

### 📈 C. Robot Trading (EA / Algorithmic Trading)

**Contoh:** Bot trading forex/emas di MetaTrader, bot crypto

**Yang sudah disiapkan:**
- **Rem darurat otomatis** — kalau rugi mencapai batas harian, bot BERHENTI sendiri
- Batas risiko per transaksi (maksimal 1% modal)
- API key trading **dilarang punya izin penarikan** — dana tetap aman walau key bocor

### 🏢 D. Sistem Enterprise (Backend Lengkap)

**Contoh:** Sistem inti perusahaan, platform multi-cabang

**Yang sudah disiapkan:**
- Kontrol akses berlapis (RBAC — siapa boleh akses apa)
- Persetujuan multi-level (Maker-Checker — satu orang tidak bisa bertindak sendiri)
- Jejak audit anti-manipulasi (tidak bisa dihapus/diedit)

---

## 5. Struktur Folder

Ini peta proyek Anda. **Jangan hafal semua** — cukup tahu yang penting.

```
📁 aegis-forge/
│
├── 📖 README.md              ← PANDUAN UTAMA (baca ini dulu!)
├── 🔧 SETUP.md               ← Panduan teknis detail
├── 📖 AGENTS.md              ← "Buku aturan" untuk AI & developer
├── 🤝 CONTRIBUTING.md         ← Cara berkontribusi
├── 🚨 SECURITY.md            ← Cara melaporkan masalah keamanan
├── ⌨️ Makefile               ← Kumpulan perintah singkat
├── 🐳 docker-compose.yml     ← Layanan lokal (database, dll)
│
├── 📁 docs/                  ← 📚 SEMUA PANDUAN & TEMPLATE
│   ├── 📁 blueprints/        ← 🏗️ Cetakan arsitektur per jenis proyek
│   │   ├── web-application-blueprint.md    (untuk Web)
│   │   ├── mobile-application-blueprint.md (untuk Mobile)
│   │   └── ea-trading-blueprint.md         (untuk Trading)
│   │
│   ├── 📁 agent-playbooks/   ← 🤖 Panduan langkah-demi-langkah untuk AI
│   ├── 📁 security/          ← 🔐 Checklist keamanan per domain
│   ├── 📁 adr/               ← 📝 Keputusan arsitektur + analisis risiko
│   ├── 📁 diagrams/          ← 🎨 Diagram arsitektur visual
│   │
│   ├── PRD-template.md       ← Template "apa yang mau dibuat"
│   ├── PRD-detail-template.md← Template detail fitur
│   ├── schema-template.sql   ← Template database (JANGAN diubah!)
│   ├── schema.sql            ← Database aktif proyek (BOLEH diubah)
│   ├── openapi-template.yaml ← Template kontrak API
│   ├── openapi.yaml          ← Kontrak API aktif proyek
│   ├── ui-design-template.md ← Template desain tampilan
│   └── prompt-library.md     ← 💬 Contoh perintah siap pakai untuk AI
│
├── 📁 evals/                 ← 🧪 Tes kualitas output AI
└── 📁 scripts/               ← ⚙️ Script otomatis (buat proyek, cek keamanan)
    ├── init-new-project.sh   ← Buat proyek baru (Linux/Mac)
    ├── init-new-project.ps1  ← Buat proyek baru (Windows)
    └── devsec-check.sh       ← Cek keamanan manual
```

### 📌 File yang Paling Sering Anda Sentuh

| File | Fungsi | Kapan Diubah |
|---|---|---|
| `docs/PRD.md` | Apa yang mau dibuat | Di awal proyek |
| `docs/schema.sql` | Struktur database | Saat menambah tabel (menu, orders, dll) |
| `docs/openapi.yaml` | Kontrak API | Saat menambah endpoint |
| `docs/ui-design.md` | Desain tampilan | Saat merancang tampilan |

### 📌 File yang JANGAN Diubah

| File | Kenapa |
|---|---|
| `*-template.*` (semua template) | Ini cetakan asli — kalau diubah, Anda kehilangan referensi bersih |
| `AGENTS.md` | Ini kontrak kerja AI — mengubahnya bisa merusak perilaku AI |
| `.github/workflows/` | Ini CI otomatis — mengubah tanpa paham bisa merusak keamanan |

---

## 6. Keamanan Bawaan

Anda **tidak perlu jadi ahli keamanan** — perlindungan ini sudah aktif sejak awal.

### 🛡️ A. Alarm Kebocoran Otomatis (Gitleaks)

**Apa yang terjadi:** Setiap kali Anda menyimpan perubahan (`git commit`), sistem otomatis memindai kode. Jika ada password atau API key yang tertinggal, **commit DITOLAK**.

**Analogi:** Seperti **metal detector di bandara** — kalau ada barang berbahaya, Anda tidak boleh masuk.

### 🔒 B. Penyimpanan Mobile Terenkripsi

**Apa yang terjadi:** Di Android, data sensitif (token login, dll) disimpan di **brankas khusus perangkat** (Keystore), bukan di file biasa yang mudah dibaca.

**Analogi:** Seperti **menyimpan uang di brankas bank**, bukan di laci meja.

### 🛑 C. Rem Darurat Trading

**Apa yang terjadi:** Kalau robot trading rugi mencapai batas harian (mis. 5% modal), sistem **otomatis berhenti trading**.

**Analogi:** Seperti **rem darurat kereta** — kalau ada bahaya, berhenti dulu, pikir nanti.

### 📜 D. Jejak Audit Anti-Manipulasi

**Apa yang terjadi:** Setiap aksi penting dicatat di database, dan catatan itu **TIDAK BISA dihapus atau diedit** — bahkan oleh admin.

**Analogi:** Seperti **tinta permanen** — sekali ditulis, tidak bisa dihapus.

### 🚫 E. API Key Trading Terbatas

**Apa yang terjadi:** API key untuk robot trading **dilarang** memiliki izin penarikan dana.

**Analogi:** Seperti **kartu ATM yang hanya bisa cek saldo** — tidak bisa tarik tunai.

---

## 7. Tutorial Membuat Proyek

Ini bagian terpenting. Ikuti langkah demi langkah.

### 📋 Prasyarat (Yang Harus Ada di Komputer Anda)

| Yang Dibutuhkan | Fungsi | Cara Cek |
|---|---|---|
| **Git** | Menyalin & melacak proyek | Buka terminal, ketik `git --version` |
| **VS Code** (disarankan) | Editor untuk menulis/melihat kode | Sudah terinstall? |
| **Docker** (opsional tapi disarankan) | Menjalankan database & layanan | `docker --version` |

> 💡 **Cara termudah:** Buka folder aegis-forge di **VS Code**, lalu klik **"Reopen in Container"** saat muncul notifikasi. Semua alat akan terinstall otomatis.

### 🚀 LANGKAH 1: Salin Template ke Komputer

Buka **terminal** (PowerShell di Windows, Terminal di Mac/Linux), lalu ketik:

```bash
# Unduh template dari GitHub
git clone https://github.com/mochrzlf/aegis-forge.git

# Masuk ke folder
cd aegis-forge
```

### 🚀 LANGKAH 2: Buat Proyek Baru Anda

Pilih **satu** perintah sesuai jenis proyek yang Anda mau:

#### Untuk Aplikasi Web:
```powershell
# Windows (PowerShell)
pwsh scripts/init-new-project.ps1 "NamaProyekAnda" "../NamaProyekAnda" web

# Linux/Mac/Git Bash
bash scripts/init-new-project.sh "NamaProyekAnda" "../NamaProyekAnda" web
```

#### Untuk Aplikasi Mobile:
```powershell
# Windows
pwsh scripts/init-new-project.ps1 "NamaProyekAnda" "../NamaProyekAnda" mobile

# Linux/Mac
bash scripts/init-new-project.sh "NamaProyekAnda" "../NamaProyekAnda" mobile
```

#### Untuk Robot Trading:
```powershell
# Windows
pwsh scripts/init-new-project.ps1 "NamaProyekAnda" "../NamaProyekAnda" trading

# Linux/Mac
bash scripts/init-new-project.sh "NamaProyekAnda" "../NamaProyekAnda" trading
```

#### Untuk Sistem Lengkap (Web + Backend):
```powershell
# Windows
pwsh scripts/init-new-project.ps1 "NamaProyekAnda" "../NamaProyekAnda" fullstack

# Linux/Mac
bash scripts/init-new-project.sh "NamaProyekAnda" "../NamaProyekAnda" fullstack
```

> 💡 **Ganti `"NamaProyekAnda"`** dengan nama proyek Anda. Contoh: `"WartegBot"`, `"PatientPortal"`, `"GoldScalperEA"`

### ✅ Yang Terjadi Otomatis (Anda Tidak Perlu Ngapa-ngapain)

Script di atas akan **otomatis**:

1. ✅ Menyalin semua panduan & pengaturan ke folder proyek baru
2. ✅ Mengganti nama placeholder dengan nama proyek Anda
3. ✅ Menyiapkan Git untuk melacak perubahan
4. ✅ Memasang "alarm keamanan" (mencegah API key bocor)
5. ✅ Membuat kunci keamanan unik untuk proyek Anda

### 🚀 LANGKAH 3: Tentukan Spesifikasi DULU (Penting!)

> ⚠️ **JANGAN langsung menulis kode!** Tentukan dulu APA yang mau dibuat.

Jika Anda menggunakan AI (Claude, Cursor, dll), beri perintah ini:

> *"Baca AGENTS.md. Buatkan draft docs/PRD.md dan docs/PRD-detail.md untuk proyek saya berdasarkan blueprint di docs/blueprints/. Lalu lakukan analisis keamanan STRIDE di docs/adr/ sebelum menulis kode aplikasi."*

AI akan membuat dokumen perencanaan dan menganalisis risiko keamanan **SEBELUM** mulai programming — seperti arsitek menggambar denah sebelum membangun.

### 🚀 LANGKAH 4: Tes API Tanpa Menunggu Backend

Untuk pekerjaan frontend/mobile, Anda tidak perlu menunggu backend selesai:

```bash
make mock-api
```

Ini menjalankan "server palsu" di `http://localhost:4010` yang menyajikan data contoh — sehingga frontend bisa dikerjakan paralel.

### 🚀 LANGKAH 5: Bangun Fitur Anda

Sekarang tinggal bangun. AI Anda sudah punya semua aturan (via `AGENTS.md`), contoh perintah siap pakai (di `docs/prompt-library.md`), dan alur kerja terpandu (di `docs/agent-playbooks/`).

### 🚀 LANGKAH 6: Cek Keamanan & Simpan

Sebelum menyimpan (commit), pastikan aman:

```bash
# Cek keamanan kapan saja:
make audit

# Setiap commit otomatis dipindai untuk kebocoran:
git add .
git commit -m "fitur: tambah registrasi pengguna"
```

**Selesai!** 🎉 Proyek Anda sekarang berdiri di atas fondasi yang aman.

---

## 8. Cara Kerja dengan AI

Aegis-Forge dirancang khusus untuk bekerja dengan AI coding (Claude, Cursor, Hermes, dll).

### 📖 Konsep: "Buku Aturan" untuk AI

File **`AGENTS.md`** adalah **kontrak kerja permanen** yang dibaca AI di awal setiap sesi. Ia berisi:

- Aturan keamanan yang HARUS dipatuhi
- Teknologi yang boleh digunakan
- Alur kerja yang harus diikuti
- Larangan yang tidak boleh dilanggar

### 💬 Cara Memberi Perintah yang Baik

#### ❌ Perintah yang BURUK:
> *"Buatkan saya aplikasi toko online"*

(Terlalu umum — AI akan menebak-nebak)

#### ✅ Perintah yang BAIK:
> *"Baca AGENTS.md dan docs/blueprints/web-application-blueprint.md. Buatkan PRD untuk toko online makanan dengan fitur: daftar menu, keranjang, checkout, dan notifikasi WhatsApp. Ikuti standar keamanan di docs/security-iam-policy.md."*

(Jelas, merujuk ke dokumen, dan menyebutkan standar keamanan)

### 📚 Prompt Siap Pakai

Lihat `docs/prompt-library.md` untuk contoh perintah yang sudah teruji per fase:

| Fase | Contoh Prompt |
|---|---|
| 📝 Perencanaan | "Buatkan PRD berdasarkan blueprint..." |
| 🏗️ Arsitektur | "Rancang schema database untuk..." |
| 🔐 Keamanan | "Lakukan analisis STRIDE untuk..." |
| 💻 Implementasi | "Implementasikan fitur X sesuai PRD..." |
| 🧪 Testing | "Buatkan test untuk..." |

---

## 9. Perintah Penting

Kumpulan "tombol pintar" yang sering dipakai.

### ⌨️ Perintah `make` (Shortcut)

| Perintah | Fungsi (Bahasa Awam) |
|---|---|
| `make help` | Tampilkan semua perintah yang tersedia |
| `make new` | **Buat proyek baru** dari template |
| `make audit` | **Cek keamanan** — pastikan tidak ada rahasia bocor |
| `make up` | **Nyalakan** layanan lokal (database, dll) |
| `make down` | **Matikan** semua layanan lokal |
| `make mock-api` | Jalankan **server API palsu** untuk testing |
| `make status` | Lihat status layanan yang sedang berjalan |

### 🪟 Untuk Pengguna Windows

Jika `make` tidak tersedia, gunakan PowerShell langsung:

```powershell
# Buat proyek baru
pwsh scripts/init-new-project.ps1 "NamaProyek" "../NamaProyek" web

# Cek keamanan (via Git Bash atau WSL)
bash scripts/devsec-check.sh
```

---

## 10. Studi Kasus

Contoh nyata bagaimana Aegis-Forge digunakan.

### 🍜 Studi Kasus 1: Bot WhatsApp Order Makanan

**Kebutuhan:** Anda ingin berjualan makanan di apartemen. Customer chat WA, bot membalas otomatis (menu, pilih, total harga), lalu order dikirim ke Anda.

**Cara menggunakan Aegis-Forge:**

1. **Buat proyek:** `pwsh scripts/init-new-project.ps1 "WartegBot" "../WartegBot" fullstack`
2. **Yang dipakai dari Aegis-Forge:**
   - ✅ `schema-template.sql` → rancang tabel `menu`, `orders`, `order_items`
   - ✅ `security baseline` → simpan API key WA & LLM terenkripsi
   - ✅ `AGENTS.md` → AI menulis kode dengan aman
   - ✅ `PRD-template.md` → dokumentasikan requirement bot
   - ✅ Audit trail → riwayat order tidak bisa dimanipulasi
3. **Yang ditambah sendiri:** konektor WhatsApp, integrasi LLM, logika percakapan

### 🏥 Studi Kasus 2: Portal Pasien Klinik

**Kebutuhan:** Klinik ingin pasien bisa daftar online, lihat jadwal dokter, dan terima pengingat.

**Cara menggunakan Aegis-Forge:**

1. **Buat proyek:** `pwsh scripts/init-new-project.ps1 "PatientPortal" "../PatientPortal" web`
2. **Yang dipakai:** Semua fitur web (login aman, RBAC untuk admin/dokter/pasien, audit trail untuk rekam medis)
3. **Yang ditambah:** logika bisnis klinik (booking, jadwal, notifikasi)

### 📈 Studi Kasus 3: Robot Trading Emas

**Kebutuhan:** Trader ingin bot yang otomatis trading XAUUSD dengan proteksi modal.

**Cara menggunakan Aegis-Forge:**

1. **Buat proyek:** `pwsh scripts/init-new-project.ps1 "GoldEA" "../GoldEA" trading`
2. **Yang dipakai:** Circuit breaker (rem darurat), risk limit 1% per trade, API key tanpa izin withdrawal
3. **Yang ditambah:** strategi trading spesifik (indikator, entry/exit rules)

---

## 11. FAQ

### ❓ Apakah saya harus bisa programming?

**Tidak harus.** Aegis-Forge dirancang untuk bekerja dengan AI agent. Anda jelaskan apa yang Anda mau, AI yang menulis kode — Aegis-Forge memastikan hasilnya aman dan rapi.

### ❓ Apa bedanya dengan framework seperti Laravel/Next.js?

Framework adalah **"mesin"**. Aegis-Forge adalah **"buku aturan + fondasi"** yang *melengkapi* framework pilihan Anda — fokusnya pada keamanan, kualitas, dan alur kerja yang benar.

### ❓ Apakah gratis?

**Ya.** Lisensi **Apache-2.0** — gratis untuk pribadi maupun komersial.

### ❓ Bagaimana kalau saya hanya butuh satu bagian saja?

**Boleh!** Setiap bagian (keamanan, checklist, panduan AI) bisa dipakai terpisah. Lihat folder `docs/`.

### ❓ Apakah Aegis-Forge bisa untuk proyek kecil sederhana?

**Bisa, tapi mungkin "overkill".** Aegis-Forge dirancang untuk proyek yang serius soal keamanan (ada data pengguna, uang, atau transaksi). Untuk proyek iseng/main-main, mungkin terlalu berat. Tapi untuk bisnis nyata — sangat direkomendasikan.

### ❓ Bagaimana cara update Aegis-Forge ke versi terbaru?

```bash
cd aegis-forge
git pull origin main
```

### ❓ Apakah data saya aman kalau pakai Aegis-Forge?

Aegis-Forge **menyediakan fondasi keamanan**, tapi keamanan akhir tetap tanggung jawab Anda. Aegis-Forge membantu dengan:
- ✅ Mencegah kebocoran API key (Gitleaks)
- ✅ Enkripsi data sensitif (AES-256)
- ✅ Audit trail anti-manipulasi
- ✅ Scan kerentanan otomatis (CI)

Tapi Anda tetap harus:
- ⚠️ Menjaga password & kunci master Anda
- ⚠️ Mengupdate dependensi secara berkala
- ⚠️ Mengikuti checklist keamanan di `docs/security/`

---

## 12. Troubleshooting

### 😰 Masalah 1: `make` tidak dikenali

**Gejala:** Ketik `make help` muncul error "command not found"

**Solusi:**
- **Windows:** Gunakan PowerShell version — `pwsh scripts/init-new-project.ps1 ...`
- **Mac:** Install via `brew install make`
- **Linux:** Install via `sudo apt install make` (Ubuntu/Debian)

### 😰 Masalah 2: Git tidak dikenali

**Gejala:** Ketik `git --version` muncul error

**Solusi:** Install Git dari [git-scm.com](https://git-scm.com)

### 😰 Masalah 3: Docker tidak jalan

**Gejala:** `make up` gagal

**Solusi:**
1. Pastikan Docker Desktop sudah terinstall dan **berjalan** (icon di system tray)
2. Coba restart Docker Desktop
3. Kalau masih gagal, Anda bisa skip Docker — tidak wajib untuk memulai

### 😰 Masalah 4: Commit ditolak ("secret detected")

**Gejala:** Saat `git commit`, muncul error tentang secret/password/API key

**Solusi:** Ini **fitur keamanan bekerja!** Jangan panik.
1. Cari file yang mengandung secret (biasanya `.env` atau file config)
2. Hapus secret dari file tersebut
3. Pindahkan ke `.env` yang sudah di-gitignore
4. Commit ulang

### 😰 Masalah 5: Script init-new-project error

**Gejala:** Script gagal saat membuat proyek baru

**Solusi:**
1. Pastikan Anda menjalankan dari dalam folder `aegis-forge`
2. Pastikan path tujuan (`../NamaProyek`) tidak sudah ada
3. Windows: pastikan PowerShell dijalankan dengan execution policy yang benar:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

---

## 🎯 Ringkasan Akhir

| Pertanyaan | Jawaban Singkat |
|---|---|
| **Apa itu Aegis-Forge?** | Template/cetakan siap pakai untuk membangun aplikasi dengan keamanan enterprise |
| **Untuk siapa?** | Pemula, developer, pengguna AI, trader — siapa pun yang mau memulai proyek dengan benar |
| **Gratis?** | Ya, Apache-2.0 |
| **Harus bisa coding?** | Tidak harus — dirancang untuk bekerja dengan AI |
| **Apa yang sudah disiapkan?** | Keamanan, database, audit trail, checklist, panduan AI, CI otomatis |
| **Apa yang masih harus dibangun?** | Logika bisnis spesifik Anda (fitur unik proyek Anda) |

---

## 📚 Langkah Selanjutnya

Setelah membaca panduan ini, Anda siap untuk:

1. ✅ **Coba buat proyek pertama** → Ikuti [Tutorial Langkah 1](#7-tutorial-membuat-proyek)
2. ✅ **Baca panduan teknis** → `SETUP.md`
3. ✅ **Pahami aturan AI** → `AGENTS.md`
4. ✅ **Lihat contoh prompt** → `docs/prompt-library.md`
5. ✅ **Pilih blueprint** → `docs/blueprints/` sesuai jenis proyek Anda

---

> 💡 **Ingat:** Anda tidak perlu memahami semuanya sekaligus. Mulai dari yang kecil, pelajari sambil jalan. Aegis-Forge dirancang untuk **menjaga Anda tetap di jalur yang benar**, bahkan saat Anda belum tahu semua jawabannya.

---

**Dokumen ini adalah bagian dari proyek [Aegis-Forge](https://github.com/mochrzlf/aegis-forge) — dilisensikan di bawah Apache-2.0.**

*Terakhir diperbarui: September 2026*
