# Security Access Matrix & Segregation of Duties (SoD)
## Enterprise IAM Governance & Entitlement Standard
### Banking-Grade Control Blueprint

| | |
|---|---|
| **Dokumen** | Security Access Matrix & Access Governance Policy |
| **Klasifikasi** | Internal Confidential — Security Baseline |
| **Prinsip Utama** | Least Privilege (PoLP), Segregation of Duties (SoD), Dual Control (Maker-Checker) |
| **Siklus Hidup** | Joiner, Mover, Leaver (JML) Automation |

---

## 1. Taksonomi Peran (Role Hierarchy)

| Role | Level Akses | Deskripsi & Batasan Tanggung Jawab |
|---|:---:|---|
| `superadmin` | Level 0 | Akun infrastruktur/root darurat (Emergency Break-Glass). Dilarang untuk aktivitas operasional harian. |
| `admin` | Level 1 | Administrator operasional sistem. Mengelola konfigurasi umum, bukan mutasi data finansial. |
| `support` | Level 2 | Customer support / helpdesk. Hak akses Read-Only terbatas, data PII dimaskir. |
| `member` | Level 3 | Pengguna standar / nasabah / klien. Hak akses hanya pada resource milik sendiri (Ownership Bound). |
| `guest` | Level 4 | Pengguna publik sebelum autentikasi. Hanya endpoint publik. |

---

## 2. Security Access Matrix (Entitlement Table)

| Modul / Sumber Daya | Aksi / Endpoint | `superadmin` | `admin` | `support` | `member` | `guest` | Catatan Kontrol Keamanan |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| **Autentikasi** | Login / Refresh / Logout | ✅ | ✅ | ✅ | ✅ | ✅ | Rate limited (max 5 req/min) |
| **Data Pribadi User** | Read Own Profile | ✅ | ✅ | ✅ | ✅ | ❌ | Row-Level Ownership Bound |
| **Data Pribadi User** | Read Other Profile | ✅ | ✅ | 👁️ (Masked) | ❌ | ❌ | Support hanya melihat 4 digit akhir HP/email |
| **Manajemen Role** | Promote / Demote Role | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | **Wajib Maker-Checker** |
| **Mutasi Finansial** | Request Transaksi/Tarik | ❌ | ❌ | ❌ | ✅ | ❌ | Step-Up MFA / Challenge Token |
| **Mutasi Finansial** | Approve Payout Komisi | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | **Maker dilarang menyetujui sendiri** |
| **Sistem & Config** | Edit Security Parameters | 🔒 **Dual** | ❌ | ❌ | ❌ | ❌ | Wajib audit log & dual authorization |
| **Audit Trail** | Read Audit Logs | ✅ | ✅ | ❌ | ❌ | ❌ | Read-Only (Auditor / Security Officer) |
| **Audit Trail** | Modify / Delete Audit Logs | ⛔ **FORBIDDEN** | ⛔ **FORBIDDEN** | ⛔ | ⛔ | ⛔ | **Immutable Append-Only** (Trigger Protected) |
| **Account Lifecycle** | Suspend / Terminate User | 🔒 **Dual** | 🔒 **Dual** | ❌ | ❌ | ❌ | Memicu Instant Session Kill-Switch |
| **Data Portability** | Request Erasure (UU PDP) | ✅ | ❌ | ❌ | ✅ (Own) | ❌ | Masa tenggang 30 hari |

*Keterangan: ✅ Diizinkan | ❌ Ditolak (403 Forbidden) | 👁️ Read-Only Terbatas | 🔒 **Dual** Wajib Alur Maker-Checker*

---

## 3. Aturan Segregation of Duties (SoD) — Anti-Fraud & Dual Control

Untuk mencegah penyalahgunaan wewenang (*fraud* internal atau akun admin yang terkompromi):

### Aturan SoD 1: Pemisahan Maker dan Checker (Four-Eyes Principle)
- Seorang administrator yang membuat permohonan (*Maker*) perubahan role user, penarikan dana massal, atau perubahan limit sistem **DILARANG KERAS** menyetujui (*Checker*) permintaannya sendiri.
- Database meng-enforce: `CHECK (maker_user_id <> checker_user_id)`.

### Aturan SoD 2: Pemisahan Pengembang vs Auditor
- Akun developer/engineer aplikasi tidak boleh memiliki akses langsung untuk memodifikasi log audit.
- Tabel `audit_logs` dilindungi trigger database anti-tamper yang menolak perintah `UPDATE` dan `DELETE`.

---

## 4. Siklus Hidup Identitas (JML: Joiner, Mover, Leaver)

### A. Joiner (Karyawan / User Baru)
1. Akun dibuat dengan status `active` dan role default `member` (Principle of Least Privilege).
2. Wajib memberikan persetujuan consent kebijakan privasi (`consent_given_at`).
3. Verifikasi identitas email atau OAuth sebelum sesi aktif.

### B. Mover (Perubahan Divisi / Peran)
1. Perubahan role memicu pencatatan ke tabel `approval_requests`.
2. Sesi lama dibatalkan paksa saat role baru disetujui untuk mencegah *privilege creep* (penumpukan hak akses lama).

### C. Leaver (Terminated / Resign / Suspended) — *Instant Access Kill-Switch*
1. Begitu status user diubah menjadi `terminated` atau `suspended`:
   - Trigger database otomatis membatalkan seluruh token di `refresh_tokens` (`revoked_at = NOW()`).
   - Redis session dibersihkan seketika.
   - User langsung terlempar keluar (*logged out*) dari semua device saat itu juga.

### D. Dormancy (Akun Pasif)
- Akun yang tidak memiliki aktivitas login selama **90 hari berturut-turut** otomatis terkunci menjadi status `dormant` dan membutuhkan verifikasi identitas ulang untuk reaktivasi.

---

## 5. Privileged Access & Break-Glass Protocol (CyberArk PAM Standard)

1. **Akun Darurat (Break-Glass):**
   - Disiapkan akun superadmin lokal darurat yang disimpan di vault terenkripsi untuk situasi darurat (*DRP / SSO Outage*).
2. **Alerting Seketika:**
   - Setiap kali akun berstatus privileged atau break-glass login, sistem otomatis mengirimkan alarm darurat ke Security Operations Center (SOC) / Telegram Admin.
3. **Session Timebox:**
   - Sesi privileged dibatasi maksimal 2 jam dan wajib memasukkan alasan akses (*Ticket / Incident ID*).

---

## 6. Checklist Rekonsiliasi Akses Berkala (User Access Review - UAR)

Setiap kuartal (3 bulan), jalankan checklist rekonsiliasi berikut:
- [ ] Tarik daftar user dengan status `active` dan bandingkan dengan status kepegawaian terkini.
- [ ] Verifikasi tidak ada akun `terminated` yang masih memiliki sesi atau token aktif.
- [ ] Tinjau seluruh akun yang memiliki role `admin` atau `superadmin` (apakah masih relevan).
- [ ] Verifikasi log transaksi Maker-Checker di tabel `approval_requests`.
- [ ] Ekspor bukti audit menggunakan script `scripts/devsec-check.sh`.
