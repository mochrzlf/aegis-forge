package users

import (
	"context"
	"database/sql"
	"errors"

	"github.com/aegisforge/starter-go/internal/core"
)

type Service struct {
	db *sql.DB
}

func NewService(db *sql.DB) *Service {
	return &Service{db: db}
}

type UserDTO struct {
	ID        string `json:"id"`
	Email     string `json:"email"`
	Role      string `json:"role"`
	Status    string `json:"status"`
	CreatedAt string `json:"createdAt"`
}

func (s *Service) SuspendUser(ctx context.Context, targetUserID, actorUserID string) (int64, error) {
	// 1. Anti-Self Suspend (Admin cannot lock themselves out)
	if targetUserID == actorUserID {
		return 0, errors.New("CANNOT_SUSPEND_SELF")
	}

	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return 0, err
	}
	defer tx.Rollback()

	// 2. Transition account lifecycle status to suspended
	res, err := tx.ExecContext(ctx,
		`UPDATE users SET status = 'suspended', updated_at = NOW() WHERE id = $1`, targetUserID)
	if err != nil {
		return 0, err
	}

	rowsAffected, _ := res.RowsAffected()
	if rowsAffected == 0 {
		return 0, errors.New("USER_NOT_FOUND")
	}

	// 3. JML Instant Session Kill-Switch: Revoke ALL active sessions
	tokenRes, err := tx.ExecContext(ctx,
		`UPDATE refresh_tokens SET is_revoked = TRUE WHERE user_id = $1 AND is_revoked = FALSE`, targetUserID)
	if err != nil {
		return 0, err
	}

	revokedCount, _ := tokenRes.RowsAffected()

	// 4. Audit Log
	_ = core.WriteAuditLog(ctx, s.db, &actorUserID, "user.suspended", "user:"+targetUserID, map[string]interface{}{
		"sessionsRevoked": revokedCount,
	})

	if err := tx.Commit(); err != nil {
		return 0, err
	}

	return revokedCount, nil
}

func (s *Service) GetUser(ctx context.Context, targetUserID, currentUserID, currentUserRole string) (*UserDTO, error) {
	// Anti-IDOR: Non-admin can only access their own profile
	if currentUserRole != "admin" && currentUserRole != "superadmin" {
		if targetUserID != currentUserID {
			return nil, errors.New("FORBIDDEN")
		}
	}

	row := s.db.QueryRowContext(ctx,
		`SELECT id, email, role, status, created_at FROM users WHERE id = $1`, targetUserID)

	var u UserDTO
	err := row.Scan(&u.ID, &u.Email, &u.Role, &u.Status, &u.CreatedAt)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, errors.New("NOT_FOUND")
		}
		return nil, err
	}

	return &u, nil
}
