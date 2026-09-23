# Aegis Forge — iOS Mobile Starter Skeleton (Swift / SwiftUI)

> **Enterprise-grade, security-hardened native iOS starter skeleton** adhering to the **Mobile AppSec Standard** (OWASP MASVS / Level 2 Banking Standards).

---

## 🛡️ Built-in Security Controls

| Pillar | Implementation | Technical Detail |
|---|---|---|
| **Hardware Secure Storage** | `KeychainStorage.swift` | Uses **Apple Keychain Services** (`kSecClassGenericPassword`). Bounded strictly to the physical device with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` and `kSecAttrSynchronizable = false` (never synced to iCloud). Zero plaintext in `UserDefaults`. |
| **Public Key SSL Pinning** | `CertificatePinning.swift` | Enforces SHA-256 SubjectPublicKeyInfo (SPKI) pinning via custom `URLSessionDelegate`. Rejects user-installed proxy CAs (Burp Suite, Charles) and untrusted TLS certificates. |
| **App Transport Security (ATS)** | `Info.plist` | `NSAllowsArbitraryLoads = false`. Blocks all unencrypted cleartext HTTP communications, enforcing TLS 1.3. |
| **Screen Privacy Shield** | `ScreenShieldModifier.swift` | Automatically blurs view hierarchy and overlays `PrivacyShieldView` whenever the app enters the iOS App Switcher or when active screen capture / AirPlay mirroring is detected (`UIScreen.capturedDidChangeNotification`). |
| **Jailbreak & Sandbox Integrity** | `JailbreakDetector.swift` | Multi-layer runtime audit checking filesystem artifacts (Cydia, Sileo, Zebra), sandbox container breakout write tests, and `DYLD_INSERT_LIBRARIES` dynamic linker injections. |
| **Banking API Client** | `APIClient.swift` | Pre-configured `URLSession` with cookie management for `HttpOnly` refresh tokens and standardized Aegis Forge response envelope (`{ success, data, error }`). |

---

## 📁 Architecture & File Layout

```
templates/mobile-ios/
├── Package.swift                     ← Swift Package Manager manifest
├── README.md                         ← iOS AppSec documentation
└── AegisSecureApp/
    ├── AegisSecureApp.swift          ← SwiftUI @main Application Entry Point
    ├── Info.plist                    ← Hardened ATS & Face ID usage descriptions
    ├── Security/
    │   ├── KeychainStorage.swift     ← Secure hardware keychain wrapper
    │   ├── CertificatePinning.swift  ← Public Key SPKI SHA-256 URLSessionDelegate
    │   ├── JailbreakDetector.swift   ← Runtime sandbox & jailbreak audit
    │   └── ScreenShieldModifier.swift← Privacy blur & anti-screen capture modifier
    ├── Network/
    │   ├── APIClient.swift           ← Pinned HTTPS client with token handling
    │   └── APIEndpoints.swift        ← REST API endpoints (aligned with docs/openapi.yaml)
    └── UI/
        ├── ContentView.swift         ← Sample banking dashboard with security status
        └── PrivacyShieldView.swift   ← Privacy cover view for multitasking switcher
```

---

## 🚀 Getting Started

### 1. Open in Xcode
1. Open Xcode 15+.
2. Select **File > Open** and choose the `templates/mobile-ios` folder (or open as Swift Package).
3. Select your target device (iPhone 15 / 16 or iOS Simulator).
4. Press **⌘ + R** to run.

### 2. Configure Your Backend API & Pinning
In `AegisSecureApp/Network/APIClient.swift`:
```swift
// Replace with your production domain
let client = APIClient(
    targetHost: "api.yourdomain.com",
    pinnedHashes: [
        "YOUR_PRIMARY_SPKI_SHA256_HASH=",
        "YOUR_BACKUP_ROTATION_HASH="
    ]
)
```

---

## 🔒 Mobile AppSec Verification Checklist

- [x] Tokens stored exclusively in Apple Keychain (Device Only).
- [x] No sensitive data written to `UserDefaults` or disk cache.
- [x] ATS enabled: cleartext HTTP blocked.
- [x] Public Key SSL Pinning enabled on API domains.
- [x] App Switcher snapshot leakage prevented via Privacy Shield blur.
- [x] Multi-layer jailbreak detection warning active.
