# Mobile Authentication & Token Lifecycle Sequence

This interaction sequence diagram illustrates the secure authentication flow on mobile devices utilizing Android Keystore and automated refresh token rotation:

```mermaid
sequenceDiagram
    autonumber
    actor User as 👤 Mobile User
    participant App as 📱 Mobile App (Compose/Flutter)
    participant Store as 🔐 Android Keystore
    participant Gateway as 🛡️ API Gateway (SSL Pinning)
    participant AuthAPI as ⚙️ Auth Service (Baseline)
    participant DB as 💾 PostgreSQL & Redis

    User->>App: Enter Credentials / Tap Biometrics
    App->>Gateway: POST /api/v1/auth/login (TLS 1.3 Verified)
    Gateway->>AuthAPI: Forward Request (User, Password, DeviceFingerprint)
    AuthAPI->>DB: Verify Argon2id Hash & Account Status
    DB-->>AuthAPI: Account Active & Role Valid
    AuthAPI->>AuthAPI: Generate Access Token (15m) & Refresh Token (7d)
    AuthAPI->>DB: Store Refresh Token Hash in Redis & Record Audit Log
    AuthAPI-->>Gateway: 200 OK (Access Token & Encrypted Refresh Token)
    Gateway-->>App: Authenticated Response

    App->>Store: Encrypt & Store Refresh Token in EncryptedSharedPreferences
    App-->>User: Display Home Screen (Dashboard)

    Note over App,Gateway: When Access Token Expires (After 15 Minutes)
    App->>Gateway: POST /api/v1/auth/refresh (Send Refresh Token from Keystore)
    Gateway->>AuthAPI: Validate Token & Check Revocation Status
    AuthAPI->>DB: Invalidate Old Refresh Token & Store New Token (Rotation)
    AuthAPI-->>Gateway: 200 OK (New Token Pair)
    Gateway-->>App: Receive New Token Pair
    App->>Store: Update New Token in Keystore
```
