# PRD Detail — User Stories & Acceptance Criteria

This document outlines the technical specifications and acceptance criteria for each feature module defined in `docs/PRD.md`.

---

## Module F1: Authentication & Session Management (IAM)

### User Story F1.1: User Login
> **As a** prospective or registered user,  
> **I want to** log in to the application using Google OAuth or a verified email,  
> **So that** I can access my personal dashboard securely without memorizing complex passwords.

#### Acceptance Criteria (AC):
- **AC 1**: Users can click the "Sign in with Google" button and be redirected to the Google OAuth consent screen.
- **AC 2**: Upon successful authorization, the server issues a short-lived JWT Access Token (15 minutes) and a Refresh Token stored in an `HttpOnly; Secure; SameSite=Strict` cookie.
- **AC 3**: The `refresh_token` MUST NOT be exposed in the JSON response body where it could be stored in `localStorage`.
- **AC 4**: Refresh tokens are hashed (SHA-256) before being persisted to the `refresh_tokens` table.
- **AC 5**: If authorization fails or is canceled, display an informative error message and a button to retry.

### User Story F1.2: Session Refresh & Replay Detection
> **As an** active application user,  
> **I want** my login session to be refreshed automatically in the background,  
> **So that** my workflow is not interrupted every 15 minutes.

#### Acceptance Criteria (AC):
- **AC 1**: The client calls `POST /auth/refresh` when the access token expires.
- **AC 2**: The server implements **Refresh Token Rotation (RTR)** — every time a refresh token is used, the server revokes the old token (`revoked_at`) and issues a new token pair.
- **AC 3**: If the system detects that an already revoked refresh token is reused (*token reuse/replay attack*), the server MUST revoke all active descendant sessions belonging to that user and record a security incident in `audit_logs`.

---

## Module F2: [Core Feature Name]

### User Story F2.1: [Feature Action Name]
> **As a** [User Role],  
> **I want to** [Action to perform],  
> **So that** [Benefit / Business objective].

#### Acceptance Criteria (AC):
- **AC 1**: [Valid input condition and expected result].
- **AC 2**: [Schema validation using Zod/Pydantic before data is processed].
- **AC 3**: [Server-side data ownership authorization check (Anti-IDOR)].
- **AC 4**: [Mutation recorded in audit log table].

#### Edge Cases & Error States:
1. **Unauthorized Access (IDOR Probe)**: If a user attempts to modify resources belonging to another user, the server responds with HTTP `403 Forbidden` or `404 Not Found`.
2. **Database Connection Interrupted**: Display a toast notification "Failed to process request, please try again shortly" without leaking internal stack traces.
