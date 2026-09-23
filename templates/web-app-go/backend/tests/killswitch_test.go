package tests

import (
	"context"
	"testing"

	"github.com/aegisforge/starter-go/internal/modules/users"
)

func TestAntiSelfSuspendRule(t *testing.T) {
	adminID := "admin_12345"
	targetID := "admin_12345" // Same user!

	service := users.NewService(nil)
	_, err := service.SuspendUser(context.Background(), targetID, adminID)

	if err == nil {
		t.Fatal("Expected error when admin attempts to suspend themselves")
	}

	if err.Error() != "CANNOT_SUSPEND_SELF" {
		t.Fatalf("Expected CANNOT_SUSPEND_SELF error, got: %v", err)
	}
}
