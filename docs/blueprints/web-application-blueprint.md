# Web Application Architecture Blueprint

This document is the technical blueprint for designing and building enterprise-grade **Modern Web & SaaS Applications** based on this Baseline.

---

## 🏛️ 1. Layered Web Architecture Pattern

The web application enforces strict Separation of Concerns across architectural layers:

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

## 🔐 2. Web Authentication & Session Management Standards

### 2.1 Secure Token Transport
- **Access Token:** JWT (JSON Web Token) format, short-lived (**maximum 15 minutes**). Stored in client application JavaScript memory (*in-memory*), NEVER in `localStorage`.
- **Refresh Token:** Opaque token with moderate validity (e.g., 7 days) backed by the `refresh_tokens` database table.
- **Cookie Delivery:** The backend MUST issue refresh tokens via the `Set-Cookie` header with the following parameters:
  ```http
  Set-Cookie: refresh_token=abc123xyz...; Path=/api/v1/auth; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
  ```
  *(These flags block JavaScript/XSS script access and mitigate Cross-Site Request Forgery attacks)*.

### 2.2 Automatic Refresh Token Rotation (RFC 6749)
Each time the `/api/v1/auth/refresh` endpoint is invoked:
1. The previous refresh token is immediately revoked.
2. A new refresh token is issued.
3. If an already revoked token is submitted, the system triggers token reuse detection (*token reuse detection*) and immediately invalidates all active sessions for that user.

---

## 🛡️ 3. Frontend Hardening

1. **Content Security Policy (CSP):**
   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.yourdomain.com; frame-ancestors 'none';
   ```
2. **Input Sanitization & Anti-XSS:**
   - All dynamic input rendered into the DOM must be sanitized using DOMPurify or the framework's native auto-escaping mechanisms (React JSX / Vue templates).
3. **Strict CORS (Cross-Origin Resource Sharing):**
   - The backend explicitly allows only trusted origin domains, disallowing wildcard (`*`) origins on authenticated endpoints.

---

## ⚡ 4. Performance & Core Web Vitals (CWV)

- **Largest Contentful Paint (LCP):** < 2.5 seconds (Next/Image optimization, WebP/AVIF formats, font preloading).
- **Interaction to Next Paint (INP):** < 200 ms (minimize long tasks on the JavaScript main thread).
- **Cumulative Layout Shift (CLS):** < 0.1 (assign explicit dimensions to image and ad elements).

---

## 📋 5. Web Release Verification Checklist

- [ ] All API endpoints enforce server-side schema validation via Zod/Pydantic.
- [ ] Security headers (*Helmet / CSP / HSTS*) are enabled and pass verification on `securityheaders.com`.
- [ ] No API keys or backend secrets are leaked into client JavaScript bundles (`NEXT_PUBLIC_` prefixes reserved strictly for non-sensitive public metadata).
- [ ] Accessibility audits comply with WCAG 2.1 AA standards (Lighthouse Accessibility Score > 90).
