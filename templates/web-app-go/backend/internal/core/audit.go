package core

import (
	"context"
	"database/sql"
	"encoding/json"
)

func WriteAuditLog(ctx context.Context, db *sql.DB, actorUserID *string, action, resource string, details map[string]interface{}) error {
	detailsJSON, err := json.Marshal(details)
	if err != nil {
		detailsJSON = []byte("{}")
	}

	query := `INSERT INTO audit_logs (actor_user_id, action, resource, details, created_at)
	          VALUES ($1, $2, $3, $4, NOW())`

	_, err = db.ExecContext(ctx, query, actorUserID, action, resource, detailsJSON)
	return err
}
