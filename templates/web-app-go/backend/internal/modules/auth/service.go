package auth

import (
	"context"
	"database/sql"
	"errors"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
	"github.com/google/uuid"
)

type Service struct {
	db               *sql.DB
	jwtAccessSecret  string
	jwtRefreshSecret string
}

func NewService(db *sql.DB, accessSecret, refreshSecret string) *Service {
	return &Service{
		db:               db,
		jwtAccessSecret:  accessSecret,
		jwtRefreshSecret: refreshSecret,
	}
}

type UserRecord struct {
	ID                  string
	Email               string
	PasswordHash        string
	Role                string
	Status              string
	FailedLoginAttempts int
	LockedUntil         *time.Time
}

type TokenPair struct {
	AccessToken  string
	RefreshToken string
	User         UserRecord
}

func (s *Service) Authenticate(ctx context.Context, email, password string) (*TokenPair, error) {
	row := s.db.QueryRowContext(ctx,
		`SELECT id, email, password_hash, role, status, failed_login_attempts, locked_until 
		 FROM users WHERE email = $1`, email)

	var u UserRecord
	err := row.Scan(&u.ID, &u.Email, &u.PasswordHash, &u.Role, &u.Status, &u.FailedLoginAttempts, &u.LockedUntil)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("INVALID_CREDENTIALS")
		}
		return nil, err
	}

	// 1. Account Lockout Check
	if u.LockedUntil != nil && u.LockedUntil.After(time.Now()) {
		return nil, errors.New("ACCOUNT_LOCKED")
	}

	// 2. Account Lifecycle Status Check
	if u.Status != "active" {
		return nil, errors.New("ACCOUNT_INACTIVE")
	}

	// 3. Verify Password
	if !core.VerifyPassword(password, u.PasswordHash) {
		newAttempts := u.FailedLoginAttempts + 1
		var lockUntil *time.Time
		if newAttempts >= 5 {
			t := time.Now().Add(15 * time.Minute)
			lockUntil = &t
		}

		_, _ = s.db.ExecContext(ctx,
			`UPDATE users SET failed_login_attempts = $1, locked_until = $2, updated_at = NOW() WHERE id = $3`,
			newAttempts, lockUntil, u.ID)

		_ = core.WriteAuditLog(ctx, s.db, &u.ID, "auth.login_failed", "user:"+u.ID, map[string]interface{}{
			"attempts": newAttempts,
			"locked":   lockUntil != nil,
		})

		if lockUntil != nil {
			return nil, errors.New("ACCOUNT_LOCKED")
		}
		return nil, errors.New("INVALID_CREDENTIALS")
	}

	// Reset lockout on successful authentication
	_, _ = s.db.ExecContext(ctx,
		`UPDATE users SET failed_login_attempts = 0, locked_until = NULL, updated_at = NOW() WHERE id = $1`,
		u.ID)

	// 4. Issue Token Pair with Rotation & Replay Family ID
	familyID := uuid.New().String()
	jti := uuid.New().String()

	accessToken, err := core.CreateAccessToken(u.ID, u.Role, s.jwtAccessSecret)
	if err != nil {
		return nil, err
	}

	refreshToken, err := core.CreateRefreshToken(u.ID, u.Role, jti, familyID, s.jwtRefreshSecret)
	if err != nil {
		return nil, err
	}

	tokenHash := core.HashToken(refreshToken)
	expiresAt := time.Now().Add(7 * 24 * time.Hour)

	_, err = s.db.ExecContext(ctx,
		`INSERT INTO refresh_tokens (user_id, token_hash, family_id, is_revoked, expires_at, created_at)
		 VALUES ($1, $2, $3, FALSE, $4, NOW())`,
		u.ID, tokenHash, familyID, expiresAt)
	if err != nil {
		return nil, err
	}

	_ = core.WriteAuditLog(ctx, s.db, &u.ID, "auth.login_success", "user:"+u.ID, map[string]interface{}{
		"familyId": familyID,
	})

	return &TokenPair{
		AccessToken:  accessToken,
		RefreshToken: refreshToken,
		User:         u,
	}, nil
}

func (s *Service) Refresh(ctx context.Context, rawRefreshToken string) (string, string, error) {
	claims, err := core.VerifyJWT(rawRefreshToken, s.jwtRefreshSecret)
	if err != nil {
		return "", "", errors.New("INVALID_TOKEN")
	}

	tokenHash := core.HashToken(rawRefreshToken)

	row := s.db.QueryRowContext(ctx,
		`SELECT id, user_id, family_id, is_revoked, expires_at 
		 FROM refresh_tokens WHERE token_hash = $1`, tokenHash)

	var tokenID, userID, familyID string
	var isRevoked bool
	var expiresAt time.Time

	err = row.Scan(&tokenID, &userID, &familyID, &isRevoked, &expiresAt)
	if err != nil {
		return "", "", errors.New("INVALID_TOKEN")
	}

	// 1. REPLAY ATTACK DETECTION (ADR-002)
	// If an already-revoked token is used again, revoke the ENTIRE family immediately!
	if isRevoked {
		_, _ = s.db.ExecContext(ctx,
			`UPDATE refresh_tokens SET is_revoked = TRUE WHERE family_id = $1`, familyID)

		_ = core.WriteAuditLog(ctx, s.db, &userID, "security.token_replay_detected", "refresh_token:"+tokenID, map[string]interface{}{
			"familyId": familyID,
			"action":   "revoked_all_family_sessions",
		})

		return "", "", errors.New("TOKEN_REPLAY_DETECTED")
	}

	if time.Now().After(expiresAt) {
		return "", "", errors.New("TOKEN_EXPIRED")
	}

	// 2. Revoke current token
	_, _ = s.db.ExecContext(ctx,
		`UPDATE refresh_tokens SET is_revoked = TRUE WHERE id = $1`, tokenID)

	// 3. Issue NEW Token Pair in the same family
	newJTI := uuid.New().String()
	newAccess, err := core.CreateAccessToken(userID, claims.Role, s.jwtAccessSecret)
	if err != nil {
		return "", "", err
	}

	newRefresh, err := core.CreateRefreshToken(userID, claims.Role, newJTI, familyID, s.jwtRefreshSecret)
	if err != nil {
		return "", "", err
	}

	newTokenHash := core.HashToken(newRefresh)
	newExpiresAt := time.Now().Add(7 * 24 * time.Hour)

	_, err = s.db.ExecContext(ctx,
		`INSERT INTO refresh_tokens (user_id, token_hash, family_id, is_revoked, expires_at, created_at)
		 VALUES ($1, $2, $3, FALSE, $4, NOW())`,
		userID, newTokenHash, familyID, newExpiresAt)
	if err != nil {
		return "", "", err
	}

	return newAccess, newRefresh, nil
}

func (s *Service) Logout(ctx context.Context, rawRefreshToken string) error {
	tokenHash := core.HashToken(rawRefreshToken)
	_, err := s.db.ExecContext(ctx,
		`UPDATE refresh_tokens SET is_revoked = TRUE WHERE token_hash = $1`, tokenHash)
	return err
}

func (s *Service) Unlock(ctx context.Context, userID string) error {
	_, err := s.db.ExecContext(ctx,
		`UPDATE users SET failed_login_attempts = 0, locked_until = NULL, updated_at = NOW() WHERE id = $1`, userID)
	return err
}
