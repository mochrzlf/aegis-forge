# Mobile Application Architecture Blueprint (Android & iOS)

Dokumen ini adalah cetak biru teknis untuk merancang dan membangun **Aplikasi Mobile Enterprise (Native Android/Kotlin, Flutter, atau React Native)** yang terhubung dengan Baseline Backend.

---

## 🏛️ 1. Pola Clean Architecture Mobile

Aplikasi mobile mengadopsi struktur Clean Architecture untuk memisahkan UI, logika bisnis, dan interaksi data:

```
[Presentation Layer]
  ├── UI Components (Jetpack Compose / Flutter Widgets)
  ├── ViewModels / State Holders (StateFlow / BLoC / Riverpod)
  └── Navigation & Deep Linking
           │
           ▼
[Domain Layer (Murni Logika Bisnis, Tanpa Ketergantungan OS)]
  ├── Use Cases / Interactors (e.g. LoginUseCase, TransferFundUseCase)
  ├── Domain Models & Business Validation
  └── Repository Interfaces (Contract)
           │
           ▼
[Data Layer]
  ├── Repository Implementations
  ├── Local Data Source:
  │     ├── Android Keystore + EncryptedSharedPreferences (Token & Auth State)
  │     └── Encrypted Room / SQLCipher (Offline Cache Database)
  └── Remote Data Source:
        ├── Retrofit / Ktor Client (OkHttp Engine + Certificate Pinner)
        └── REST API Contract (docs/openapi.yaml)
```

---

## 🔐 2. Standar Keamanan Mobile Enterprise (Mobile AppSec)

### 2.1 Penyimpanan Kredensial Aman (Hardware Keystore)
- ❌ **Dilarang Keras:** Menyimpan token autentikasi di plain `SharedPreferences`, `NSUserDefaults`, atau file teks unencrypted.
- ✅ **Standar Android Native:**
  Gunakan `EncryptedSharedPreferences` dengan master key yang dikelola oleh hardware-backed **Android Keystore System**:
  ```kotlin
  val masterKey = MasterKey.Builder(context)
      .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
      .build()

  val securePreferences = EncryptedSharedPreferences.create(
      context,
      "secure_app_prefs",
      masterKey,
      EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
      EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
  )
  ```
- ✅ **Standar Flutter / React Native:**
  Gunakan plugin `flutter_secure_storage` (Android Keystore + iOS Keychain) atau `react-native-keychain`.

### 2.2 SSL / Certificate Pinning (Anti-Man-in-the-Middle)
Untuk mencegah sniffing trafik jaringan pada WiFi publik atau proxy:
- Di Android, buat file `res/xml/network_security_config.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <network-security-config>
      <domain-config cleartextTrafficPermitted="false">
          <domain includeSubdomains="true">api.yourdomain.com</domain>
          <pin-set expiration="2027-01-01">
              <!-- SHA-256 Public Key Pinning -->
              <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
              <!-- Backup Pin untuk antisipasi rotasi sertifikat -->
              <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
          </pin-set>
      </domain-config>
  </network-security-config>
  ```
- Di `AndroidManifest.xml`:
  ```xml
  <application android:networkSecurityConfig="@xml/network_security_config" ... >
  ```

### 2.3 Proteksi Layar Sensitif (`FLAG_SECURE`)
Pada Activity atau Composable yang menampilkan informasi rahasia (saldo, nomor kartu, OTP, form ganti sandi):
```kotlin
// Android Activity
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    window.setFlags(
        WindowManager.LayoutParams.FLAG_SECURE,
        WindowManager.LayoutParams.FLAG_SECURE
    )
}
```
*Efek:* Layar menjadi hitam saat direkam atau di-screenshot, dan disamarkan pada tampilan Android *Recent Apps*.

### 2.4 Obfuscation & Minifikasi (R8 / ProGuard)
Konfigurasikan `android/app/build.gradle.kts`:
```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

---

## ⚡ 3. Alur Kerja Offline-First & Mock Testing

1. **Sinkronisasi Data Lokal:** Gunakan pola *Single Source of Truth* di mana UI hanya mengamati data dari database lokal (Room/SQLCipher), dan layer jaringan bertugas menyinkronkan data ke backend.
2. **Pengujian Cepat Tanpa Menunggu Backend:**
   - Jalankan `make mock-api` di Baseline (port 4010).
   - Arahkan `BASE_URL` Android di emulator ke `http://10.0.2.2:4010/api/v1` (IP loopback host dari emulator Android) untuk langsung menguji request & response API.

---

## 📋 4. Checklist Kesiapan Google Play Store (Data Safety)

- [ ] Cleartext traffic dinonaktifkan (`cleartextTrafficPermitted="false"`).
- [ ] Tidak ada file sertifikat rilis `.jks`, `.keystore`, atau `google-services.json` yang ter-commit ke Git (diverifikasi oleh Gitleaks).
- [ ] Target SDK selalu menggunakan versi Android terbaru sesuai kebijakan Play Console.
- [ ] Pengumpulan data PII memenuhi deklarasi privasi sesuai `docs/security-iam-policy.md`.
