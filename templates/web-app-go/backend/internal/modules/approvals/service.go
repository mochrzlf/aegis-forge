package approvals

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"

	"github.com/aegisforge/starter-go/internal/core"
)

var (
	ErrMakerCannotBeChecker = errors.New("MAKER_CANNOT_BE_CHECKER")
	ErrNotFound             = errors.New("NOT_FOUND")
	ErrAlreadyResolved      = errors.New("ALREADY_RESOLVED")
)

type Service struct {
	db *sql.DB
}

func NewService(db *sql.DB) *Service {
	return &Service{db: db}
}

type ApprovalRequest struct {
	ID             string                 `json:"id"`
	MakerUserID    string                 `json:"makerUserId"`
	CheckerUserID  *string                `json:"checkerUserId,omitempty"`
	ActionType     string                 `json:"actionType"`
	Payload        map[string]interface{} `json:"payload"`
	Status         string                 `json:"status"`
	DecisionReason *string                `json:"decisionReason,omitempty"`
	CreatedAt      string                 `json:"createdAt"`
	ReviewedAt     *string                `json:"reviewedAt,omitempty"`
}

func (s *Service) CreateRequest(ctx context.Context, makerUserID, actionType string, payload map[string]interface{}) (string, error) {
	payloadJSON, err := json.Marshal(payload)
	if err != nil {
		return "", err
	}

	var newID string
	err = s.db.QueryRowContext(ctx,
		`INSERT INTO approval_requests (maker_user_id, action_type, payload, status, created_at)
		 VALUES ($1, $2, $3, 'pending', NOW())
		 RETURNING id`, makerUserID, actionType, payloadJSON).Scan(&newID)

	if err != nil {
		return "", err
	}

	_ = core.WriteAuditLog(ctx, s.db, &makerUserID, "approval.created", "approval:"+newID, map[string]interface{}{
		"actionType": actionType,
	})

	return newID, nil
}

func (s *Service) ReviewRequest(ctx context.Context, requestID, checkerUserID, decision, reason string) error {
	// 1. Fetch Request
	row := s.db.QueryRowContext(ctx,
		`SELECT maker_user_id, status FROM approval_requests WHERE id = $1`, requestID)

	var makerID, currentStatus string
	err := row.Scan(&makerID, &currentStatus)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return errors.New("NOT_FOUND")
		}
		return err
	}

	if currentStatus != "pending" {
		return errors.New("ALREADY_RESOLVED")
	}

	// 2. Maker-Checker Four-Eyes Principle: Maker CANNOT approve own request
	if makerID == checkerUserID {
		return errors.New("MAKER_CANNOT_BE_CHECKER")
	}

	// 3. Update DB (Constraint chk_maker_not_checker also enforces this at database level)
	_, err = s.db.ExecContext(ctx,
		`UPDATE approval_requests 
		 SET checker_user_id = $1, status = $2, decision_reason = $3, reviewed_at = NOW() 
		 WHERE id = $4`, checkerUserID, decision, reason, requestID)

	if err != nil {
		return err
	}

	_ = core.WriteAuditLog(ctx, s.db, &checkerUserID, "approval."+decision, "approval:"+requestID, map[string]interface{}{
		"makerId": makerID,
		"reason":  reason,
	})

	return nil
}
