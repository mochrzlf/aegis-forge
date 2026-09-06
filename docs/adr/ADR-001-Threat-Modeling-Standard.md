# ADR-001: Standar Otomasi Threat Modeling (STRIDE)
## Architecture Decision Record

| | |
|---|---|
| **ID** | ADR-001 |
| **Judul** | Penerapan Otomasi STRIDE Threat Modeling Sebelum Implementasi Fitur |
| **Status** | **ACCEPTED** |
| **Tanggal** | September 2026 |
| **Diputuskan oleh** | Lead Cyber Security Architect & Founder |
| **Berdampak pada** | Seluruh proses pengembangan software & AI Agent workflow |

---

## 1. Konteks Masalah
Pengembangan aplikasi yang cepat sering kali mengabaikan celah keamanan pada fase desain awal (*shift-left security*). Developer atau AI Agent cenderung langsung menulis kode (*happy path*) tanpa mempertimbangkan skenario penyalahgunaan (*abuse cases*), IDOR, atau bypass otorisasi.

## 2. Keputusan
Ditetapkan bahwa **setiap fitur, modul, endpoint baru, atau perubahan skema database WAJIB didahului analisis STRIDE Threat Modeling**.
- Analisis dituangkan dalam dokumen ADR di folder `docs/adr/`.
- AI Coding Agent (Hermes Agent) tidak diizinkan menulis kode sebelum mitigasi keamanan disepakati dalam analisis ancaman tersebut.

## 3. Konsekuensi
- **Positif:** Kode yang dihasilkan memiliki standar keamanan enterprise, minim kerentanan OWASP Top 10, dan memiliki dokumentasi keamanan yang lengkap untuk kebutuhan audit.
- **Trade-off:** Menambah waktu perencanaan awal sekitar 2-5 menit sebelum penulisan kode dimulai. Trade-off ini dinilai sangat sepadan dibandingkan biaya memperbaiki kerentanan di tahap produksi.
