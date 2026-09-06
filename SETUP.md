# Panduan Setup Project Baru dari Baseline

Dokumen ini menjelaskan langkah demi langkah untuk membuat project baru menggunakan Baseline ini.

---

## 1. Buat Salinan Project Baru

Gunakan shortcut alias atau script otomatis:
```bash
# Menggunakan shortcut alias
new-project "MyAwesomeApp" "/home/tpam_su/Project/MyAwesomeApp"

# Atau jalankan script langsung
bash /home/tpam_su/Project/Baseline/scripts/init-new-project.sh "MyAwesomeApp" "/home/tpam_su/Project/MyAwesomeApp"
cd /home/tpam_su/Project/MyAwesomeApp
```

Script akan otomatis:
1. Menyalin seluruh struktur baseline (`AGENTS.md`, `docs/`, `scripts/`, `.env.example`, `.gitignore`, `docker-compose.yml`, `.github/`).
2. Mengganti nama placeholder `[PROJECT_NAME]` menjadi nama project Anda di semua file template.
3. Menginisialisasi Git repository baru (`git init -b main`).
4. Memasang dan mengaktifkan **Git Pre-Commit Security Hook** (`.git/hooks/pre-commit`) untuk mencegah kebocoran file `.env`, private key, dan secret token via Gitleaks.
5. Menyiapkan `.env` lokal dari `.env.example`.

---

## 2. Siapkan Environment Variables

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

Sistem keamanan sudah terintegrasi secara otomatis:
- **Git Pre-Commit Hook**: Berjalan otomatis setiap kali Anda melakukan `git commit`, memverifikasi bahwa tidak ada file `.env`, file private key, atau secret token yang ter-staged.
- **Manual Audit**: Anda dapat menjalankan audit keamanan menyeluruh kapan saja dengan:
  ```bash
  devsec-check
  # atau
  bash scripts/devsec-check.sh
  ```

---

## 6. Shortcut Perintah di Terminal

Beberapa alias praktis yang telah terdaftar di `~/.bashrc`:
- `hermes` : Membuka Hermes AI Agent di terminal CLI.
- `hermes-ui` : Menjalankan web dashboard Hermes (`http://127.0.0.1:9119`).
- `new-project <Nama> <Path>` : Membuat project baru dari template baseline.
- `goto-baseline` : Langsung berpindah ke direktori Baseline.
- `devsec-check` : Menjalankan audit keamanan DevSecOps.
