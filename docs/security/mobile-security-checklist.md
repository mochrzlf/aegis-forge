# Enterprise Mobile Application Security Checklist

This checklist is mandatory for both developers and AI Agents before any mobile application (Android/iOS) is released to staging environments or app stores (Google Play Store / Apple App Store).

---

## 🔒 1. Cryptography & Local Data Storage (Data Storage & Privacy)

- [ ] **M1.1: Zero Plaintext Credential Storage**  
  No tokens, passwords, or personally identifiable information (PII / national ID / full name) are stored in plaintext `SharedPreferences`, `NSUserDefaults`, or standard `.txt`/`.json` files.
- [ ] **M1.2: Hardware Keystore Enforcement**  
  Session credential storage utilizes `EncryptedSharedPreferences` with master keys generated via the **Android Keystore System** (AES-256-GCM / AES-256-SIV).
- [ ] **M1.3: Local Database Encryption**  
  Local SQLite/Room databases storing transaction data or offline profiles are encrypted using **SQLCipher** with encryption keys derived from the Keystore.
- [ ] **M1.4: Screen Protection (`FLAG_SECURE`)**  
  The `FLAG_SECURE` window flag is enabled across all Activities displaying sensitive data (preventing screenshots, screen recordings, and task switcher preview leaks in recent apps).

---

## 🌐 2. Network Security & Communications

- [ ] **M2.1: Cleartext Traffic Disabled**  
  `cleartextTrafficPermitted="false"` is declared in `network_security_config.xml`. All network communications must enforce HTTPS (TLS 1.3).
- [ ] **M2.2: Certificate Pinning Active**  
  Public Key Pinning (SPKI SHA-256) is configured across all primary API domain endpoints with valid backup pins.
- [ ] **M2.3: Anti-MitM Validation**  
  The application rejects user-installed certificates (*user-installed CA / proxy certificates*) such as Burp Suite, Charles Proxy, or mitmproxy in release builds.

---

## 🛡️ 3. Device & App Integrity Protection (Runtime Protection)

- [ ] **M3.1: Root & Jailbreak Detection**  
  The application verifies device integrity status during startup. If root/Magisk/jailbreak access is detected, the application issues a warning and restricts financial/sensitive transactions.
- [ ] **M3.2: Play Integrity / SafetyNet API Verification**  
  The application leverages the Google Play Integrity API to validate that the application binary is untampered (*genuine app binary*) and running in a genuine Android environment.
- [ ] **M3.3: Emulator Detection**  
  The application detects execution within emulators during critical transaction flows.
- [ ] **M3.4: R8 / ProGuard Obfuscation**  
  Minification and code obfuscation for classes, methods, and field names are active in release builds (`isMinifyEnabled = true`, `isShrinkResources = true`).

---

## 🔑 4. Mobile Authentication & Session Management

- [ ] **M4.1: Short-Lived Access Token**  
  Access tokens expire in a maximum of 15 minutes.
- [ ] **M4.2: Biometric Challenge Integration**  
  High-value operations (transfers, payments, email/password changes) trigger the official `BiometricPrompt` (CryptoObject bound to a hardware Keystore key).
- [ ] **M4.3: Remote Session Kill-Switch**  
  When a user account is suspended or terminated on the backend, the application immediately clears local tokens and redirects the user to the Login screen.

---

## 🚫 5. Secret Leak Prevention (DevSecOps)

- [ ] **M5.1: No Hardcoded Keystore Secrets**  
  Keystore passwords, aliases, and `.jks / .keystore` signing files MUST NOT exist in Git repositories.
- [ ] **M5.2: Gitleaks Pre-Commit Check Passed**  
  All staged commits pass Gitleaks security scans before being pushed to remote.
