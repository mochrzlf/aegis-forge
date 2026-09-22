# Aegis Forge — Android Mobile Starter Skeleton

Security-hardened native Android starter skeleton adhering to the **Mobile AppSec Standard**.

---

## 🛡️ Built-in Security Controls

1. **Hardware-Backed Keystore Storage (`SecureStorage.kt`)**:
   - Uses `EncryptedSharedPreferences` backed by `MasterKey` (AES256-GCM / AES256-SIV).
   - Zero plaintext token storage in SharedPreferences.

2. **Public Key Pinning & Anti-Cleartext (`network_security_config.xml`)**:
   - `cleartextTrafficPermitted="false"` blocks unencrypted HTTP calls.
   - Enforces SHA-256 Public Key Pinning on backend APIs with backup rotation pin.

3. **Screen Capture Protection (`BaseSecureActivity.kt`)**:
   - Sets `WindowManager.LayoutParams.FLAG_SECURE` across all sensitive views.
   - Blocks screenshots, screen recordings, and obscures recent-apps switcher previews.

4. **Code Obfuscation & Minification (`proguard-rules.pro`)**:
   - R8 minification enabled for release builds.
   - Strips logging statements (`Log.d`, `Log.v`, `Log.i`) from release APKs.

---

## 🚀 Building & Testing

```bash
# Open in Android Studio or build with Gradle wrapper
./gradlew check
./gradlew assembleRelease
```
