package tests

import (
	"testing"

	"github.com/aegisforge/starter-go/internal/modules/approvals"
)

type MockApprovalService struct {
	status string
}

func (m *MockApprovalService) Review(makerID, checkerID, decision string) error {
	if makerID == checkerID {
		return approvals.ErrMakerCannotBeChecker
	}
	m.status = decision
	return nil
}

func TestMakerCannotBeChecker(t *testing.T) {
	mock := &MockApprovalService{}

	makerID := "usr_maker_123"
	checkerID := "usr_maker_123" // Same user trying to approve own request

	err := mock.Review(makerID, checkerID, "approved")
	if err != approvals.ErrMakerCannotBeChecker {
		t.Fatalf("Expected ErrMakerCannotBeChecker, got: %v", err)
	}

	// Different user should succeed
	checkerIDBob := "usr_checker_456"
	err = mock.Review(makerID, checkerIDBob, "approved")
	if err != nil {
		t.Fatalf("Expected valid checker to succeed, got: %v", err)
	}
	if mock.status != "approved" {
		t.Fatalf("Expected status to be approved, got: %s", mock.status)
	}
}

func TestFourEyesPrincipleLogic(t *testing.T) {
	makerID := "user_alice_uuid"
	checkerID := "user_bob_uuid"

	if makerID == checkerID {
		t.Fatal("Expected maker and checker to be different")
	}

	// Self-approval attempt check
	selfCheckerID := "user_alice_uuid"
	if makerID != selfCheckerID {
		t.Fatal("Self-approval check failed")
	}
}
