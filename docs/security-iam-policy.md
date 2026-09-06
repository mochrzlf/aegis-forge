# Enterprise Security & IAM Policy Blueprint
## Standar Keamanan Identitas, Akses, dan Perlindungan Data

Dokumen ini adalah pedoman formal arsitektur keamanan bagi tim engineer dan AI Agent dalam merancang, membangun, dan menguji sistem.

---

## 1. Identitas & Autentikasi (Authentication)

1. **Password Policy (Jika Ada Local Auth):**
   - Wajib menggunakan algoritma hashing **Argon2id** (pilihan utama) atau **bcrypt** (cost factor minimal 12).
   - Minimal 12 karakter dengan kombinasi huruf besar, kecil, angka, dan simbol.
   - Pengecekan terhadap daftar kebocoran password umum (*HaveIBeenPwned API check*).
2. **Session & Token Hygiene:**
   - **Access Token:** Berumur sangat pendek (maksimal 15 menit), stateless JWT berisi klaim: `sub` (User ID), `role`, dan `jti` (JWT ID unik).
   - **Refresh Token:** Wajib disimpan di database dalam bentuk SHA-256 hash.
   - **Transport Cookie:** Wajib dikirimkan melalui header `Set-Cookie` dengan flag:
     `HttpOnly; Secure; SameSite=Strict; Path=/api/auth`.
   - DILARANG KERAS menyimpan token autentikasi di `localStorage` atau `sessionStorage`.
3. **Refresh Token Rotation (RTR):**
   - Setiap penggunaan refresh token menghasilkan token baru dan membatalkan token sebelumnya.
   - Jika token yang sudah di-revoke dipanggil kembali, sistem memicu **Replay Detection Alert**, membatalkan seluruh sesi turunan, dan mencatat event ke `audit_logs`.

---

## 2. Otorisasi & Kontrol Akses (Authorization & IAM)

1. **Principle of Least Privilege (PoLP):**
   - Pengguna dan service hanya diberikan izin minimum mutlak yang dibutuhkan untuk menjalankan tugasnya.
2. **Role-Based Access Control (RBAC):**
   - Hierarki Role:
     - `superadmin`: Manajemen sistem global, konfigurasi keamanan, dan audit.
     - `admin`: Manajemen operasional dan review pengguna.
     - `support`: Akses read-only terbatas untuk tiket keluhan (data sensitif dimaskir).
     - `member`: Pengguna standar pemilik data akun sendiri.
     - `guest`: Akses publik read-only.
3. **Pencegahan IDOR (Insecure Direct Object Reference / BOLA):**
   - Server tidak boleh hanya memvalidasi apakah format `id` valid.
   - Server WAJIB memvalidasi bahwa `id` resource yang diminta benar-benar milik pengguna yang sedang login (`WHERE id = :id AND user_id = :currentUserId`).
4. **Step-Up Authentication:**
   - Untuk aksi kritis (penarikan saldo, perubahan peran pengguna, ekspor data massal, hapus akun), pengguna wajib melalui tantangan autentikasi ulang (re-enter password, OTP WhatsApp/Email, atau WebAuthn).

---

## 3. Threat Modeling (STRIDE) SOP

Setiap pembuatan endpoint atau penambahan modul baru wajib didahului evaluasi STRIDE:

| Kategori Ancaman | Fokus Evaluasi | Mitigasi Standar |
|---|---|---|
| **S**poofing | Pemalsuan identitas / sesi | Validasi signature JWT, verifikasi webhook HMAC |
| **T**ampering | Modifikasi data ilegal | Zod input validation, database constraints, parameterized query |
| **R**epudiation | Penyangkalan aksi | Pencatatan permanen ke `audit_logs` (IP, UA, Timestamp) |
| **I**nformation Disclosure | Kebocoran data rahasia | Masking PII, generic error messages, Field-Level Encryption |
| **D**enial of Service | Exhaustion resource | Redis rate-limiter, pagination wajib, payload size limits |
| **E**levation of Privilege | Lompatan hak akses | Server-side role guard, Row-Level Security / IDOR check |

Dokumentasikan hasil evaluasi di `docs/adr/ADR-[NUM]-threat-model-[fitur].md`.

---

## 4. Kepatuhan Regulasi (UU Perlindungan Data Pribadi No. 27/2022)

1. **Persetujuan Pemrosesan Data (Consent):**
   - Wajib mencatat waktu dan versi kebijakan privasi yang disetujui saat onboarding (`consent_given_at`, `consent_policy_version`).
2. **Hak Penghapusan Data (Right to Erasure):**
   - Pengguna berhak meminta penghapusan akun.
   - Diberikan masa tenggang 30 hari (`deletion_requested_at`). Setelah 30 hari, background worker menjalankan *Permanent Hard Delete* atau *Anonymization* pada data riwayat.
3. **Data Portability:**
   - Menyediakan fitur download arsip data akun dalam format terstruktur (JSON/CSV terenkripsi).
4. **Enkripsi Kredensial Pihak Ketiga (Field-Level Encryption):**
   - Token pihak ketiga (Gmail, GitHub, Payment Gateway) wajib dienkripsi di level kolom menggunakan **AES-256-GCM**.
