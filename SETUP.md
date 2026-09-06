# Panduan Setup Project Baru dari Baseline

Dokumen ini menjelaskan langkah demi langkah untuk membuat project baru menggunakan Baseline ini.

---

## 1. Buat Salinan Project Baru

Gunakan script otomatis:
```bash
bash /home/tpam_su/Project/Baseline/scripts/init-new-project.sh "MyAwesomeApp" "/home/tpam_su/Project/MyAwesomeApp"
cd /home/tpam_su/Project/MyAwesomeApp
```

Script akan:
1. Menyalin seluruh struktur baseline (`AGENTS.md`, `docs/`, `scripts/`, `.env.example`).
2. Mengganti nama placeholder `[PROJECT_NAME]` menjadi nama project Anda.
3. Menginisialisasi git repository baru.

---

## 2. Siapkan Environment Variables

```bash
cp .env.example .env
```
Buka `.env` dan sesuaikan nilainya:
- Generate JWT Secret: `openssl rand -base64 48`
- Generate Encryption Master Key: `openssl rand -hex 32`
- Konfigurasikan koneksi PostgreSQL dan Redis.

---

## 3. Tahap Perancangan Produk (PRD & UI Design)

Sebelum menulis kode aplikasi:
1. Isi `docs/PRD.md` (gunakan `docs/PRD-template.md` sebagai acuan).
2. Tentukan modul dan acceptance criteria di `docs/PRD-detail.md`.
3. Tentukan palet warna brand di `docs/ui-design.md`.
4. Sesuaikan endpoint API di `docs/openapi.yaml`.
5. Sesuaikan tabel database di `docs/schema.sql`.

Anda bisa meminta Hermes Agent melakukannya:
> *"Hermes, tolong lengkapi docs/PRD.md dan docs/ui-design.md untuk website portal kesehatan pasien berbasis template baseline."*

---

## 4. Setup Database & Migrasi

Jalankan script skema PostgreSQL:
```bash
# Menggunakan psql lokal
psql -U postgres -d my_awesome_app_dev -f docs/schema.sql
```

---

## 5. Menjalankan Security Pre-Flight Check

Pastikan tidak ada kredensial yang bocor sebelum mulai commit:
```bash
bash scripts/devsec-check.sh
```
