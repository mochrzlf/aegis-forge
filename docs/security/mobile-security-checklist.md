# Enterprise Mobile Application Security Checklist

Checklist ini wajib dipenuhi oleh developer maupun AI Agent sebelum aplikasi mobile (Android/iOS) dirilis ke lingkungan staging atau toko aplikasi (Google Play Store / Apple App Store).

---

## 🔒 1. Kriptografi & Penyimpanan Data Lokal (Data Storage & Privacy)

- [ ] **M1.1: Zero Plaintext Credential Storage**  
  Tidak ada token, password, atau identitas pribadi (NIK/nama lengkap) yang disimpan dalam plain `SharedPreferences`, `NSUserDefaults`, atau file `.txt`/`.json` biasa.
- [ ] **M1.2: Hardware Keystore Enforcement**  
  Penyimpanan kredensial sesi menggunakan `EncryptedSharedPreferences` dengan kunci yang di-generate melalui **Android Keystore System** (AES-256-GCM / AES-256-SIV).
- [ ] **M1.3: Database Enkripsi Lokal**  
  Database SQLite/Room lokal yang menampung data transaksi atau profil offline dienkripsi menggunakan **SQLCipher** dengan kunci yang diturunkan dari Keystore.
- [ ] **M1.4: Screen Protection (`FLAG_SECURE`)**  
  Window flag `FLAG_SECURE` aktif pada seluruh Activity yang menampilkan data sensitif (mencegah screenshot, screen recording, dan blur saat recent apps).

---

## 🌐 2. Keamanan Jaringan & Komunikasi (Network Security)

- [ ] **M2.1: Cleartext Traffic Disabled**  
  `cleartextTrafficPermitted="false"` dideklarasikan di `network_security_config.xml`. Semua komunikasi wajib melewati HTTPS (TLS 1.3).
- [ ] **M2.2: Certificate Pinning Active**  
  Public Key Pinning (SPKI SHA-256) dikonfigurasi untuk seluruh endpoint domain API utama dengan sertifikat backup yang valid.
- [ ] **M2.3: Anti-MitM Validation**  
  Aplikasi menolak sertifikat buatan (*user-installed CA / proxy certificates*) seperti Burp Suite, Charles Proxy, atau mitmproxy pada build release.

---

## 🛡️ 3. Integritas Aplikasi & Proteksi Runtime (Device & App Integrity)

- [ ] **M3.1: Root & Jailbreak Detection**  
  Aplikasi memverifikasi status integritas perangkat saat inisialisasi awal. Jika terdeteksi akses root/magisk/jailbreak, aplikasi memberikan peringatan dan membatasi transaksi finansial.
- [ ] **M3.2: Play Integrity / SafetyNet API Verification**  
  Aplikasi memanfaatkan Google Play Integrity API untuk memvalidasi bahwa binary aplikasi tidak dimodifikasi (*genuine app binary*) dan berjalan di lingkungan Android resmi.
- [ ] **M3.3: Emulator Detection**  
  Aplikasi mendeteksi eksekusi di dalam emulator saat menjalankan flow transaksi kritis.
- [ ] **M3.4: R8 / ProGuard Obfuscation**  
  Minifikasi dan pengaburan nama class, method, dan variabel aktif pada build release (`isMinifyEnabled = true`, `isShrinkResources = true`).

---

## 🔑 4. Manajemen Autentikasi & Sesi Mobile

- [ ] **M4.1: Short-Lived Access Token**  
  Access token kedaluwarsa maksimal dalam 15 menit.
- [ ] **M4.2: Biometric Challenge Integration**  
  Aksi bernilai tinggi (transfer, pembayaran, perubahan email/password) memicu `BiometricPrompt` resmi (CryptoObject terikat pada Keystore key).
- [ ] **M4.3: Remote Session Kill-Switch**  
  Saat akun pengguna di-suspend atau di-terminate di backend, aplikasi otomatis membuang token lokal dan mengarahkan pengguna kembali ke halaman Login.

---

## 🚫 5. Anti-Kebocoran Rahasia (DevSecOps)

- [ ] **M5.1: No Hardcoded Keystore Secrets**  
  Password keystore, alias, dan file `.jks / .keystore` TIDAK berada di repositori Git.
- [ ] **M5.2: Gitleaks Pre-Commit Check Passed**  
  Seluruh staged commit lolos pemindaian Gitleaks sebelum dikirim ke remote.
