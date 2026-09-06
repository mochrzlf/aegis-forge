-- =============================================================================
-- HARDENED POSTGRESQL DATABASE SCHEMA BASELINE
-- PostgreSQL 14+
-- Enterprise Banking Standard IAM & Cyber Security Baseline
-- =============================================================================
-- Built-in Security Features:
--  1. pgcrypto (UUIDv4) & CITEXT (Case-Insensitive Email)
--  2. Role-Based Access Control (RBAC) & User Status Lifecycle (JML)
--  3. Maker-Checker (Dual Control / Four-Eyes Principle) Table
--  4. Token Rotation (RTR) & Hash Storage (Anti-Replay Attack)
--  5. Immutable Audit Trail (Anti-Tamper: Update & Delete Blocked)
--  6. Instant Kill-Switch Trigger on User Termination
--  7. Field-Level Encryption Store for Third-Party Credentials (AES-256-GCM)
--  8. Compliance with Data Privacy Laws (e.g., GDPR) (Right to Erasure / 30-Day Grace Period)
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- -----------------------------------------------------------------------------
-- 0. ENUM TYPES
-- -----------------------------------------------------------------------------
CREATE TYPE user_role AS ENUM (
    'superadmin',      -- Root / Break-Glass Emergency
    'admin',           -- Operations Administrator
    'support',         -- Customer Support (Masked Read-Only)
    'member',          -- Standard User
    'guest'            -- Public User
);

CREATE TYPE user_status AS ENUM (
    'active',          -- Normal active user
    'suspended',       -- Temporarily suspended due to investigation/anomaly
    'dormant',         -- Inactive > 90 days (auto-lock)
    'terminated'       -- Permanently deactivated (instant session revocation)
);

CREATE TYPE audit_action AS ENUM (
    'auth.login_success',
    'auth.login_failed',
    'auth.token_refresh',
    'auth.token_replay_detected',
    'auth.logout',
    'auth.break_glass_access',
    'user.create',
    'user.update_profile',
    'user.change_role_requested',
    'user.change_role_approved',
    'user.status_changed',
    'user.request_deletion',
    'approval.requested',
    'approval.approved',
    'approval.rejected',
    'security.step_up_challenge',
    'security.sod_violation_blocked',
    'data.create',
    'data.update',
    'data.delete'
);

CREATE TYPE audit_status AS ENUM ('SUCCESS', 'FAILURE');
CREATE TYPE approval_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED');

-- -----------------------------------------------------------------------------
-- 1. USERS TABLE (Identity Lifecycle & JML Ready)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email                   CITEXT NOT NULL UNIQUE,
    name                    VARCHAR(120) NOT NULL,
    password_hash           VARCHAR(255),                  -- Argon2id / bcrypt
    role                    user_role NOT NULL DEFAULT 'member',
    status                  user_status NOT NULL DEFAULT 'active',
    avatar_url              TEXT,
    
    -- Security & Account Health
    failed_login_attempts   INT NOT NULL DEFAULT 0,
    locked_until            TIMESTAMPTZ,
    last_login_at           TIMESTAMPTZ,
    password_changed_at     TIMESTAMPTZ DEFAULT now(),
    email_verified_at       TIMESTAMPTZ,
    
    -- Data Privacy Laws Compliance (e.g., GDPR) (Consent & Right to Erasure)
    consent_given_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    consent_policy_version  VARCHAR(20) NOT NULL DEFAULT 'v1.0',
    deletion_requested_at   TIMESTAMPTZ,                   -- 30-day grace period
    
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_status ON users(role, status);

-- -----------------------------------------------------------------------------
-- 2. DUAL CONTROL / MAKER-CHECKER (Segregation of Duties Enforced)
-- -----------------------------------------------------------------------------
CREATE TABLE approval_requests (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_type             VARCHAR(60) NOT NULL,          -- e.g., 'user.role_change', 'payout.disburse'
    target_entity_type      VARCHAR(50) NOT NULL,          -- 'users', 'finance', 'system_config'
    target_entity_id        VARCHAR(64) NOT NULL,
    payload                 JSONB NOT NULL,                -- Proposed change payload
    maker_user_id           UUID NOT NULL REFERENCES users(id),
    checker_user_id         UUID REFERENCES users(id),
    status                  approval_status NOT NULL DEFAULT 'PENDING',
    rejection_reason        VARCHAR(255),
    expires_at              TIMESTAMPTZ NOT NULL,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at             TIMESTAMPTZ,
    
    -- Strict SoD Rule: Maker MUST NOT be the Checker for their own request!
    CONSTRAINT chk_maker_checker_different CHECK (maker_user_id <> checker_user_id)
);
CREATE INDEX idx_approvals_status ON approval_requests(status, expires_at);
CREATE INDEX idx_approvals_maker ON approval_requests(maker_user_id);

-- -----------------------------------------------------------------------------
-- 3. REFRESH TOKENS (RFC 6749 Compliant + Replay Detection)
-- -----------------------------------------------------------------------------
CREATE TABLE refresh_tokens (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash              VARCHAR(128) NOT NULL UNIQUE,  -- SHA-256 hash of raw refresh token
    device_name             VARCHAR(50),                   -- "Chrome on Windows", "Mobile App"
    ip_address              INET,
    expires_at              TIMESTAMPTZ NOT NULL,
    rotated_from_id         UUID REFERENCES refresh_tokens(id),
    revoked_at              TIMESTAMPTZ,
    revoked_reason          VARCHAR(100),                  -- "user_logout", "user_terminated", "replay_detected"
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_refresh_tokens_hash ON refresh_tokens(token_hash);

-- -----------------------------------------------------------------------------
-- 4. IMMUTABLE AUDIT TRAIL (Anti-Tamper / Compliance-Ready)
-- -----------------------------------------------------------------------------
CREATE TABLE audit_logs (
    id                      BIGSERIAL PRIMARY KEY,
    request_id              VARCHAR(64),                   -- Distributed trace / correlation ID
    user_id                 UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_role              user_role,
    action                  audit_action NOT NULL,
    status                  audit_status NOT NULL DEFAULT 'SUCCESS',
    reason_code             VARCHAR(60),                   -- 'AUTH_FAILURE', 'SOD_BLOCKED', 'RATE_LIMITED'
    entity_type             VARCHAR(50) NOT NULL,
    entity_id               VARCHAR(64),
    ip_address              INET,
    user_agent              VARCHAR(300),
    metadata                JSONB,                         -- MUST NOT contain PII or raw passwords!
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_user_time ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_action_time ON audit_logs(action, created_at DESC);
CREATE INDEX idx_audit_status ON audit_logs(status, created_at DESC);

-- ANTI-TAMPER PROTECTION: Audit logs CANNOT be UPDATED or DELETED by anyone!
CREATE OR REPLACE FUNCTION protect_audit_logs()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'TAMPER ATTEMPT BLOCKED: Audit logs are immutable and cannot be updated or deleted!';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_audit_logs
    BEFORE UPDATE OR DELETE ON audit_logs
    FOR EACH ROW
    EXECUTE PROCEDURE protect_audit_logs();

-- -----------------------------------------------------------------------------
-- 5. THIRD-PARTY ENCRYPTED CREDENTIALS (Field-Level Encryption / AES-256-GCM)
-- -----------------------------------------------------------------------------
CREATE TABLE third_party_credentials (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name            VARCHAR(50) NOT NULL,          -- e.g., "google_oauth", "broker_api"
    encrypted_payload       TEXT NOT NULL,                 -- Base64 AES-256-GCM encrypted
    iv                      VARCHAR(32) NOT NULL,          -- Hex IV (12 bytes / 24 hex)
    auth_tag                VARCHAR(32) NOT NULL,          -- Hex GCM Tag (16 bytes / 32 hex)
    created_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_user_service UNIQUE (user_id, service_name)
);

-- -----------------------------------------------------------------------------
-- 6. AUTOMATED JML TRIGGER: LEAVER KILL-SWITCH
-- -----------------------------------------------------------------------------
-- Once user status changes to 'terminated' or 'suspended', 
-- the system automatically revokes all active sessions and refresh tokens immediately!
CREATE OR REPLACE FUNCTION trigger_user_status_kill_switch()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.status IN ('terminated', 'suspended')) AND (OLD.status NOT IN ('terminated', 'suspended')) THEN
        UPDATE refresh_tokens
        SET revoked_at = NOW(),
            revoked_reason = CONCAT('JML_ACTION_', UPPER(NEW.status::TEXT))
        WHERE user_id = NEW.id AND revoked_at IS NULL;
        
        -- Record JML incident in audit trail
        INSERT INTO audit_logs (user_id, actor_role, action, status, entity_type, entity_id, metadata)
        VALUES (NEW.id, NEW.role, 'user.status_changed', 'SUCCESS', 'users', NEW.id::TEXT, 
                jsonb_build_object('old_status', OLD.status, 'new_status', NEW.status, 'revocation', 'INSTANT_KILL_SWITCH'));
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_user_kill_switch
    AFTER UPDATE OF status ON users
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_user_status_kill_switch();

-- -----------------------------------------------------------------------------
-- 7. AUTO-UPDATE UPDATED_AT TIMESTAMP TRIGGER
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_timestamp_users
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TRIGGER set_timestamp_credentials
    BEFORE UPDATE ON third_party_credentials
    FOR EACH ROW
    EXECUTE PROCEDURE trigger_set_timestamp();
