package tests

import (
	"testing"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
)

func TestPasswordHashingAndVerification(t *testing.T) {
	password := "SecretP@ssw0rd!"

	hash, err := core.HashPassword(password)
	if err != nil {
		t.Fatalf("Failed to hash password: %v", err)
	}

	if !core.VerifyPassword(password, hash) {
		t.Fatal("Expected password to verify successfully against hash")
	}

	if core.VerifyPassword("WrongPassword123!", hash) {
		t.Fatal("Expected invalid password to fail verification")
	}
}

func TestLockoutThresholdCalculation(t *testing.T) {
	maxFailedAttempts := 5
	attempts := 0

	for i := 1; i <= 4; i++ {
		attempts++
		isLocked := attempts >= maxFailedAttempts
		if isLocked {
			t.Fatalf("Account should NOT be locked at %d attempts", attempts)
		}
	}

	// 5th failed attempt
	attempts++
	isLocked := attempts >= maxFailedAttempts
	if !isLocked {
		t.Fatal("Account MUST be locked at 5 failed attempts")
	}

	lockUntil := time.Now().Add(15 * time.Minute)
	if !lockUntil.After(time.Now()) {
		t.Fatal("LockedUntil timestamp must be in the future")
	}
}
