# Aegis Forge — Web App (Next.js + Supabase) — OPT-IN ALTERNATIVE

> ⚠️ **READ THIS FIRST — this template deviates from the default security stance.**
>
> The default, **Recommended** web skeleton is [`templates/web-app/`](../web-app/)
> (FastAPI + Postgres + Redis). It enforces the full AGENTS.md §4.1 / ADR-002
> stance: **Refresh Token Rotation (RTR), HttpOnly+Secure+SameSite=Strict cookie,
> replay detection with descendant-session revocation, append-only audit_logs,
> no external vendor dependency.**
>
> **This `web-app-nextjs-supabase` template trades some of that stance for a
> full-stack frontend and managed infrastructure. It is an OPT-IN alternative,
> not the recommended default.** See "Security stance deviations" below before
> choosing it.

## When to use this template
- You need a **real frontend (UI)** out of the box (Next.js App Router + Tailwind).
- You accept **Supabase** as a managed auth+DB vendor (speed over portability).
- You are building a solo/MVP product where time-to-first-page matters more
  than the strictest auth posture.

## Security stance deviations (honest, non-negotiable to disclose)

| Stance (default skeleton) | This template | Why it matters |
|---|---|---|
| RTR + **replay detection + revoke all descendant sessions on reuse** | Supabase rotates refresh tokens (`enable_refresh_token_rotation=true` in `config.toml`) but does NOT implement replay-detection with descendant-session revocation like the FastAPI skeleton does. | A leaked/replayed refresh token is not auto-contained to the same degree. |
| Refresh token ONLY in `HttpOnly;Secure;SameSite=Strict` cookie, never localStorage | Supabase stores session client-side by default; this template uses `@supabase/ssr` **server-side cookie** to *approach* the stance, but SameSite/rotation semantics differ. | Token theft surface is larger than the default. |
| No external vendor dependency (Dependency Gate) | **Depends on Supabase (managed cloud) OR `supabase start` (local stack, heavy).** | Violates the Dependency Gate → this template is **Reference Only**, never the Recommended default. |
| Append-only `audit_logs` (DB trigger) | Provided as an equivalent Postgres trigger in `supabase/migrations/`. | Preserved — good. |
| RBAC / anti-IDOR via server code | Via **Row Level Security (RLS)** policies in Postgres. | Equivalent protection, different mechanism (declarative vs imperative). |

> If any of the auth deviations is unacceptable for your project, **use
> `templates/web-app/` instead** (optionally add a Next.js frontend to it).
> Choosing this template is an explicit acceptance of the deviations above.

## Stack
- **Next.js 14+ (App Router) + TypeScript + Tailwind CSS**
- **Supabase** — Auth (GoTrue), Postgres, Row Level Security
- **`@supabase/ssr`** — server-side session (cookie) for RSC/route handlers
- **Docker** — local Supabase stack via `supabase start` (or point at cloud)
- **CI** — gitleaks / semgrep / trivy, actions pinned to real SHAs

## Layout
```
web-app-nextjs-supabase/
├── README.md                      ← this file
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── next.config.mjs
├── tailwind.config.ts
├── postcss.config.mjs
├── middleware.ts                  ← session refresh on every request
├── app/
│   ├── layout.tsx
│   ├── page.tsx                   ← public landing
│   ├── globals.css
│   ├── (auth)/login/page.tsx
│   ├── (auth)/register/page.tsx
│   ├── (protected)/dashboard/page.tsx   ← RLS-protected example
│   └── auth/callback/route.ts     ← OAuth/email confirm callback
├── lib/
│   └── supabase/
│       ├── client.ts              ← browser client
│       ├── server.ts              ← server (RSC/route handler) client
│       └── middleware.ts          ← session-refresh helper
├── supabase/
│   ├── config.toml
│   └── migrations/
│       └── 0001_init.sql          ← profiles table + RLS + append-only audit_logs
├── Makefile
└── .github/workflows/security.yml
```

## Quick start
```bash
cp .env.example .env.local        # fill NEXT_PUBLIC_SUPABASE_URL + ANON_KEY
npm install
# Option A — local Supabase stack (needs Docker + supabase CLI):
npx supabase start                 # prints local URL + anon key to put in .env.local
# Option B — Supabase cloud project: paste its URL + anon key into .env.local
npm run dev                        # http://localhost:3000
```

## How to extend (token-economy rule)
1. PRD via `prd-interviewer` → `docs/PRD.md`; tasks via `spec-to-tasks` → `docs/TASKS.md`.
2. Each task EDITS existing files. New table → add migration + RLS policy in
   `supabase/migrations/`; new page → add under `app/(protected)/`.
3. Do NOT bypass RLS from the client with a service-role key. The service-role
   key must never ship to the browser.

## Out of scope (deliberately)
- No service-role / admin backend (RLS-only access from the app).
- No production deploy config (Vercel/Railway) — see the deferred CLI/ADR backlog.
- Auth posture here is Supabase's, NOT the FastAPI skeleton's RTR stance.
