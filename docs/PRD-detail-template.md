# PRD Detail — User Stories & Acceptance Criteria

Dokumen ini menjabarkan spesifikasi teknis dan kriteria penerimaan untuk setiap modul fitur yang didefinisikan di `docs/PRD.md`.

---

## Modul F1: Autentikasi & Manajemen Sesi (IAM)

### User Story F1.1: Login Pengguna
> **Sebagai** calon pengguna baru atau pengguna terdaftar,  
> **Saya ingin** masuk ke aplikasi menggunakan Google OAuth atau email terverifikasi,  
> **Agar** saya bisa mengakses dashboard pribadi secara aman tanpa menghafal password rumit.

#### Acceptance Criteria (AC):
- **AC 1**: Pengguna dapat menekan tombol "Masuk dengan Google" dan diarahkan ke consent screen OAuth Google.
- **AC 2**: Saat otorisasi berhasil, server menerbitkan short-lived JWT Access Token (15 menit) dan Refresh Token yang disimpan dalam cookie `HttpOnly; Secure; SameSite=Strict`.
- **AC 3**: DILARANG mengekspos `refresh_token` ke dalam JSON response body yang dapat disimpan di `localStorage`.
- **AC 4**: Token refresh di-hash (SHA-256) sebelum disimpan ke tabel `refresh_tokens`.
- **AC 5**: Jika otorisasi gagal atau dibatalkan, tampilkan pesan error yang informatif dan tombol untuk mencoba kembali.

### User Story F1.2: Refresh Sesi & Replay Detection
> **Sebagai** pengguna yang sedang aktif menggunakan aplikasi,  
> **Saya ingin** sesi login saya diperbarui secara otomatis di latar belakang,  
> **Agar** pekerjaan saya tidak terputus setiap 15 menit.

#### Acceptance Criteria (AC):
- **AC 1**: Client memanggil `POST /auth/refresh` saat access token kedaluwarsa.
- **AC 2**: Server menerapkan **Refresh Token Rotation (RTR)** — setiap kali refresh token digunakan, server membatalkan token lama (`revoked_at`) dan menerbitkan pasangan token baru.
- **AC 3**: Jika sistem mendeteksi refresh token yang sudah pernah di-revoke digunakan kembali (*token reuse/replay attack*), server WAJIB membatalkan seluruh sesi turunan milik pengguna tersebut dan mencatat insiden keamanan ke `audit_logs`.

---

## Modul F2: [Nama Core Feature]

### User Story F2.1: [Nama Aksi Fitur]
> **Sebagai** [Role Pengguna],  
> **Saya ingin** [Aksi yang ingin dilakukan],  
> **Agar** [Manfaat / Tujuan bisnis].

#### Acceptance Criteria (AC):
- **AC 1**: [Kondisi input valid dan hasil yang diharapkan].
- **AC 2**: [Validasi schema menggunakan Zod/Pydantic sebelum data diproses].
- **AC 3**: [Pengecekan otorisasi kepemilikan data (Anti-IDOR) di level server].
- **AC 4**: [Pencatatan mutasi ke tabel audit log].

#### Edge Cases & Error States:
1. **Akses tanpa hak (IDOR Probe)**: Jika user mencoba memodifikasi resource milik user lain, server merespons dengan HTTP `403 Forbidden` atau `404 Not Found`.
2. **Koneksi database terputus**: Tampilkan notifikasi toast "Gagal memproses permintaan, silakan coba beberapa saat lagi" tanpa membocorkan stacktrace internal.
