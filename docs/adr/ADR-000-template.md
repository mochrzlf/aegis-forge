# ADR-[NUM]: [Judul Keputusan Arsitektur]
## Architecture Decision Record & Threat Model

| | |
|---|---|
| **ID** | ADR-[NUM] |
| **Judul** | [Judul Keputusan Singkat] |
| **Status** | PROPOSED / ACCEPTED / DEPRECATED |
| **Tanggal** | [Bulan Tahun] |
| **Diputuskan oleh** | [Nama Engineer / Security Architect] |
| **Berdampak pada** | [Komponen sistem yang terdampak] |

---

## 1. Konteks Masalah
[Jelaskan latar belakang teknis atau kebutuhan bisnis yang melatarbelakangi keputusan ini].

---

## 2. Pilihan Alternatif yang Dipertimbangkan
1. **Opsi A**: [Deskripsi singkat, kelebihan & kekurangan].
2. **Opsi B**: [Deskripsi singkat, kelebihan & kekurangan].

---

## 3. Keputusan yang Diambil
[Jelaskan opsi mana yang dipilih dan dasar argumen pemilihannya].

---

## 4. Analisis Keamanan (STRIDE Threat Model)

| Kategori Ancaman | Potensi Serangan pada Fitur Ini | Rencana Mitigasi Teknis |
|---|---|---|
| **S**poofing | [Potensi pemalsuan identitas] | [Mitigasi otentikasi] |
| **T**ampering | [Potensi manipulasi parameter] | [Validasi schema / checksum] |
| **R**epudiation | [Potensi penyangkalan transaksi] | [Audit logging spesifik] |
| **I**nformation Disclosure | [Potensi kebocoran data] | [Masking / enkripsi field] |
| **D**enial of Service | [Potensi spam / abuse] | [Rate limiting per IP / User] |
| **E**levation of Privilege | [Potensi IDOR atau bypass role] | [Role guard & ownership check] |

---

## 5. Konsekuensi Positif & Negatif
- **Positif:** [Manfaat performa, kecepatan dev, atau keamanan].
- **Negatif / Trade-off:** [Kompleksitas tambahan, overhead database, dll].
