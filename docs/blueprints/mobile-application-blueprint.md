# Mobile Application Architecture Blueprint (Android & iOS)

This document is the technical blueprint for designing and building **Enterprise Mobile Applications (Native Android/Kotlin, Flutter, or React Native)** integrating with the Baseline Backend.

---

## 🏛️ 1. Clean Architecture Pattern for Mobile

The mobile application adopts Clean Architecture to decouple UI presentation, business rules, and data persistence:

```
[Presentation Layer]
  ├── UI Components (Jetpack Compose / Flutter Widgets)
  ├── ViewModels / State Holders (StateFlow / BLoC / Riverpod)
  └── Navigation & Deep Linking
           │
           ▼
[Domain Layer (Pure Business Logic, OS-Agnostic)]
  ├── Use Cases / Interactors (e.g., LoginUseCase, TransferFundUseCase)
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

## 🔐 2. Enterprise Mobile Security Standards (Mobile AppSec)

### 2.1 Secure Credential Storage (Hardware Keystore)
- ❌ **Strictly Prohibited:** Storing authentication tokens in plaintext `SharedPreferences`, `NSUserDefaults`, or unencrypted files.
- ✅ **Native Android Standard:**
  Utilize `EncryptedSharedPreferences` backed by master keys managed by the hardware-backed **Android Keystore System**:
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
- ✅ **Flutter / React Native Standard:**
  Use the `flutter_secure_storage` plugin (backed by Android Keystore + iOS Keychain) or `react-native-keychain`.

### 2.2 SSL / Certificate Pinning (Anti-Man-in-the-Middle)
To prevent network traffic sniffing and interception on public Wi-Fi or proxy environments:
- In Android, configure `res/xml/network_security_config.xml`:
  ```xml
  <?xml version="1.0" encoding="utf-8"?>
  <network-security-config>
      <domain-config cleartextTrafficPermitted="false">
          <domain includeSubdomains="true">api.yourdomain.com</domain>
          <pin-set expiration="2027-01-01">
              <!-- SHA-256 Public Key Pinning -->
              <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
              <!-- Backup Pin for certificate rotation resilience -->
              <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
          </pin-set>
      </domain-config>
  </network-security-config>
  ```
- Reference in `AndroidManifest.xml`:
  ```xml
  <application android:networkSecurityConfig="@xml/network_security_config" ... >
  ```

### 2.3 Sensitive Screen Protection (`FLAG_SECURE`)
In Activities or Composables displaying sensitive financial or personal data (account balance, card number, OTP, password reset forms):
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
*Effect:* The screen turns black when captured via screenshot or screen recording, and is obfuscated in the Android *Recent Apps* switcher.

### 2.4 Obfuscation & Minification (R8 / ProGuard)
Configure `android/app/build.gradle.kts`:
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

## ⚡ 3. Offline-First & Mock Testing Workflow

1. **Local Data Synchronization:** Adopt the *Single Source of Truth* pattern where UI components exclusively observe state from the local database (Room/SQLCipher), and the network layer reconciles data asynchronously with the backend.
2. **Rapid Testing Without Backend Dependencies:**
   - Execute `make mock-api` in the baseline project (port 4010).
   - Point the Android emulator `BASE_URL` to `http://10.0.2.2:4010/api/v1` (host loopback alias from Android emulator) to directly validate API request/response serialization.

---

## 📋 4. Google Play Store Readiness Checklist (Data Safety)

- [ ] Cleartext traffic disabled (`cleartextTrafficPermitted="false"`).
- [ ] No release signing certificates (`.jks`, `.keystore`) or `google-services.json` committed to Git (enforced via Gitleaks).
- [ ] Target SDK updated to the latest Android version mandated by Google Play Console policies.
- [ ] PII data collection adheres to privacy declarations in `docs/security-iam-policy.md` and Data Privacy Laws (e.g., GDPR).
