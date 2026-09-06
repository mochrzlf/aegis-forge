# Panduan Setup & Inisialisasi Proyek Multi-Domain

Dokumen ini menjelaskan langkah demi langkah untuk membuat proyek baru menggunakan **Universal Enterprise Baseline** (Web, Mobile, EA Trading, atau Fullstack).

---

## 1. Buat Salinan Proyek Baru Berdasarkan Domain

Gunakan perintah `make new` atau script otomatis:

```bash
# Opsi 1: Proyek Web Application / SaaS
bash scripts/init-new-project.sh "MyWebApp" "../MyWebApp" web

# Opsi 2: Proyek Mobile Application (Android / iOS)
bash scripts/init-new-project.sh "MyMobileApp" "../MyMobileApp" mobile

# Opsi 3: Proyek EA / Algorithmic Trading
bash scripts/init-new-project.sh "MyTradingEA" "../MyTradingEA" trading

# Opsi 4: Proyek Fullstack Enterprise (Default)
bash scripts/init-new-project.sh "MyFullstack" "../MyFullstack" fullstack
```

Script akan otomatis:
1. Menyalin seluruh struktur baseline (`AGENTS.md`, `docs/blueprints/`, `docs/security/`, `docs/diagrams/`, `Makefile`, `.env.example`, `.gitignore`, `.gitattributes`, `.gitleaks.toml`).
2. Mengganti nama placeholder `[PROJECT_NAME]` menjadi nama proyek Anda.
3. Menginisialisasi Git repository baru (`git init -b main`).
4. Memasang dan mengaktifkan **Git Pre-Commit Security Hook** (`.git/hooks/pre-commit`) untuk memblokir kebocoran file `.env`, file private key, keystore Android, dan secret token via Gitleaks.
5. Menyiapkan file `.env` lokal dengan kunci enkripsi & JWT unik yang di-generate otomatis via OpenSSL.

---

## 2. Siapkan Kredensial & Lingkungan (.env)

Masuk ke direktori proyek baru:
```bash
cd ../NamaProyekAnda
```
Buka file `.env` dan generate kunci kriptografi yang aman:
- Generate JWT Secret: `openssl rand -base64 48`
- Generate Encryption Master Key: `openssl rand -hex 32`
- Sesuaikan konfigurasi database atau API key sesuai domain proyek.

---

## 3. Alur Kerja Khusus per Domain

### 🌐 A. Jika Anda Membangun Proyek Web:
1. Rujuk cetak biru di `docs/blueprints/web-application-blueprint.md`.
2. Perintahkan Hermes Agent:
   > *"Hermes, tolong rancang docs/PRD.md dan docs/ui-design.md untuk aplikasi web ini dengan state management Zustand dan token session HttpOnly."*

### 📱 B. Jika Anda Membangun Proyek Mobile (Android/iOS):
1. Rujuk cetak biru di `docs/blueprints/mobile-application-blueprint.md` dan checklist di `docs/security/mobile-security-checklist.md`.
2. Jalankan Mock API Server instan:
   ```bash
   make mock-api
   ```
   *(Akses `http://localhost:4010` atau `http://10.0.2.2:4010` di emulator Android untuk langsung menguji request & response API).*
3. Perintahkan Hermes Agent:
   > *"Hermes, tolong rancang aplikasi Android Jetpack Compose dengan Clean Architecture dan simpan token di EncryptedSharedPreferences (Android Keystore)."*

### 📈 C. Jika Anda Membangun Proyek EA / Algorithmic Trading:
1. Rujuk cetak biru di `docs/blueprints/ea-trading-blueprint.md` dan kebijakan risiko di `docs/security/trading-risk-policy.md`.
2. Perintahkan Hermes Agent:
   > *"Hermes, tolong rancang arsitektur EA Trading untuk instrumen XAUUSD/EURUSD dengan aturan Hard Stop Loss, kalkulasi lot dinamis maksimal 1% risiko modal, dan Circuit Breaker jika daily drawdown mencapai 5%."*

---

## 4. Menjalankan Security Audit Kapan Saja

Sistem keamanan pre-commit hook berjalan otomatis saat Anda melakukan `git commit`. Anda juga dapat melakukan audit manual kapan saja:
```bash
make audit
# atau
devsec-check
```

---

## 5. Ringkasan Shortcut Perintah

| Shortcut | Fungsi |
| :--- | :--- |
| `make help` | Menampilkan seluruh perintah yang tersedia |
| `make audit` | Menjalankan audit keamanan Gitleaks & secret detection |
| `make mock-api` | Menjalankan mock server API (port 4010) |
| `make up` | Menjalankan stack Docker Compose lokal |
| `make down` | Menghentikan stack Docker Compose lokal |
| `make hermes` | Membuka Hermes AI Agent di terminal |
| `make hermes-ui` | Menjalankan Web Dashboard Hermes di browser (port 9119) |
| `new-project` | Shortcut alias terminal untuk membuat proyek baru |
| `goto-baseline` | Berpindah langsung ke direktori Baseline |
