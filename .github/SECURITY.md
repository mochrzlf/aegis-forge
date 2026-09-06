# Security Policy

## 🛡️ Enterprise Vulnerability Disclosure Policy

Keamanan dan privasi data adalah prioritas tertinggi dalam arsitektur **Enterprise Baseline**. Kami menyambut baik laporan dari peneliti keamanan, pengembang, dan pengguna untuk membantu menjaga integritas repositori dan aplikasi turunannya.

---

## 📦 Versi yang Didukung (Supported Versions)

Hanya rilis terbaru pada branch utama yang secara aktif menerima pembaruan keamanan:

| Versi | Didukung Secara Aktif | Status Patch Keamanan |
| :--- | :---: | :--- |
| **Main (Latest)** | ✅ Ya | Patch langsung dirilis via PR & CI/CD |
| **< 1.0.0** | ❌ Tidak | Harap rebase ke rilis terbaru |

---

## 🚨 Cara Melaporkan Kerentanan (Reporting a Vulnerability)

Jika Anda menemukan potensi kerentanan keamanan (vulnerability) atau kebocoran kredensial, **JANGAN** membuat issue publik di GitHub. Harap laporkan melalui salah satu saluran rahasia berikut:

1. **GitHub Private Vulnerability Reporting (Direkomendasikan):**
   - Masuk ke tab **Security** pada repositori GitHub.
   - Klik **Report a vulnerability** untuk membuka draf pengungkapan terenkripsi yang hanya dapat diakses oleh *maintainer*.

2. **Email Tim Keamanan:**
   - Kirimkan detail temuan ke: `security@enterprise.local` (atau kontak maintainer di profil GitHub).

### Format Laporan yang Diharapkan:
- **Deskripsi Kerentanan:** Penjelasan singkat tentang tipe celah (misal: Broken Access Control, SQL Injection, Secret Exposure, SSRF).
- **Langkah Reproduksi (Proof of Concept):** Langkah terperinci atau skrip PoC untuk memvalidasi temuan.
- **Dampak Potensial:** Risiko bisnis atau teknis jika kerentanan dieksploitasi.
- **Rekomendasi Remediasi:** Saran perbaikan kode atau konfigurasi jika tersedia.

---

## ⏱️ Service Level Agreement (SLA) Respons

Tim maintainer berkomitmen pada standar penanganan kerentanan perbankan & enterprise:

- **Pengakuan Awal (Acknowledgment):** Maksimal **1x24 jam** sejak laporan diterima.
- **Triase & Validasi:** Maksimal **3 hari kerja**.
- **Rilis Patch Keamanan (Hotfix):** 
  - *Critical / High Severity (CVSS 7.0 - 10.0):* Maksimal **7 hari kalender**.
  - *Medium / Low Severity (CVSS < 7.0):* Disertakan dalam siklus rilis berikutnya.

---

## 🔒 Kebijakan Safe Harbor & Etika Riset

Kami mendukung riset keamanan yang bertanggung jawab (*Responsible Disclosure*). Selama Anda:
1. Tidak merusak data produksi atau mengganggu ketersediaan layanan (*Denial of Service*).
2. Tidak mengakses atau mengekstrak data pribadi pengguna lain.
3. Memberikan waktu yang wajar bagi tim untuk merilis perbaikan sebelum mempublikasikan temuan ke publik.

Maka kami tidak akan menempuh jalur hukum terhadap aktivitas riset keamanan Anda.
