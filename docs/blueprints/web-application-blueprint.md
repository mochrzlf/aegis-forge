# Web Application Architecture Blueprint

Dokumen ini adalah cetak biru teknis untuk merancang dan membangun **Aplikasi Web & SaaS Modern** berskala enterprise berbasis Baseline.

---

## 🏛️ 1. Pola Arsitektur Berlapis (Layered Web Architecture)

Aplikasi web mengadopsi pemisahan tanggung jawab (*Separation of Concerns*) yang tegas:

```
[Presentation Layer]
  ├── UI Components (shadcn/ui, Radix Primitives, Tailwind CSS)
  ├── Client State (Zustand / TanStack React Query)
  └── Pages / Routing (Next.js App Router / Vue Nuxt)
           │
           ▼ (HTTPS TLS 1.3 / REST API / GraphQL)
[API Gateway & Security Layer]
  ├── Reverse Proxy (Nginx / Cloudflare / Envoy)
  ├── Rate Limiter (Redis Token Bucket)
  └── Security Headers (Helmet: Strict CSP, HSTS, X-Frame-Options)
           │
           ▼
[Backend Application Layer]
  ├── Route Controllers / Handlers (Input Validation via Zod/Pydantic)
  ├── Application Services & Use Cases (Business Logic)
  ├── Domain Entities & Value Objects
  └── Security Guards (RBAC / ABAC, Maker-Checker Interceptors)
           │
           ▼
[Infrastructure & Persistence Layer]
  ├── Database Repositories (Prisma / Drizzle ORM -> PostgreSQL 16)
  ├── Cache & Pub/Sub (Redis 7)
  └── Field-Level Encryption (AES-256-GCM)
```

---

## 🔐 2. Standar Autentikasi & Manajemen Sesi Web

### 2.1 Transport Token Aman
- **Access Token:** Format JWT (JSON Web Token), masa berlaku pendek (**maksimal 15 menit**). Disimpan di memori JavaScript aplikasi client (*in-memory*), BUKAN di `localStorage`.
- **Refresh Token:** Token opaque dengan masa berlaku moderat (misal 7 hari) yang didukung oleh tabel database `refresh_tokens`.
- **Pengiriman Cookie:** Refresh token WAJIB dikirim oleh backend via header `Set-Cookie` dengan parameter:
  ```http
  Set-Cookie: refresh_token=abc123xyz...; Path=/api/v1/auth; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
  ```
  *(Flags ini memblokir akses script JavaScript/XSS dan mencegah serangan Cross-Site Request Forgery)*.

### 2.2 Rotasi Refresh Token Otomatis (RFC 6749)
Setiap kali endpoint `/api/v1/auth/refresh` dipanggil:
1. Refresh token lama langsung di-revoke.
2. Refresh token baru diterbitkan.
3. Jika token yang sudah di-revoke mencoba digunakan kembali, sistem mendeteksi pencurian token (*token reuse detection*) dan mencabut seluruh sesi pengguna yang bersangkutan seketika.

---

## 🛡️ 3. Pengerasan Keamanan Frontend (Frontend Hardening)

1. **Content Security Policy (CSP):**
   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none';
   ```
2. **Sanitasi Input & Anti-XSS:**
   - Semua input yang dirender ke DOM wajib disanitasi menggunakan DOMPurify atau fitur auto-escaping bawaan framework (React JSX / Vue templates).
3. **CORS Ketat (Cross-Origin Resource Sharing):**
   - Backend hanya mengizinkan *origin* resmi domain web, bukan wildcard (`*`).

---

## ⚡ 4. Kinerja & Core Web Vitals (CWV)

- **Largest Contentful Paint (LCP):** < 2.5 detik (optimasi gambar Next/Image, format WebP/AVIF, preloading font).
- **Interaction to Next Paint (INP):** < 200 ms (hindari long tasks di main thread JavaScript).
- **Cumulative Layout Shift (CLS):** < 0.1 (alokasikan ukuran eksplisit pada elemen gambar dan iklan).

---

## 📋 5. Checklist Verifikasi Rilis Web

- [ ] Seluruh endpoint API tervalidasi skema Zod/Pydantic di sisi server.
- [ ] Header keamanan (*Helmet / CSP / HSTS*) aktif dan lulus uji di `securityheaders.com`.
- [ ] Tidak ada API key atau secret rahasia yang bocor ke bundle JavaScript client (`NEXT_PUBLIC_` hanya untuk data publik non-kredensial).
- [ ] Audit aksesibilitas lulus uji WCAG 2.1 AA (Lighthouse Accessibility Score > 90).
