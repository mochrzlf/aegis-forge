package tests

import (
	"testing"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
)

func TestJWTAccessTokenLifecycle(t *testing.T) {
	secret := "test_secret_key_at_least_32_bytes_long!"
	userID := "usr_998877"
	role := "member"

	tokenStr, err := core.CreateAccessToken(userID, role, secret)
	if err != nil {
		t.Fatalf("Failed to create access token: %v", err)
	}

	claims, err := core.VerifyJWT(tokenStr, secret)
	if err != nil {
		t.Fatalf("Failed to verify access token: %v", err)
	}

	if claims.UserID != userID {
		t.Fatalf("Expected UserID %s, got %s", userID, claims.UserID)
	}

	if claims.Role != role {
		t.Fatalf("Expected Role %s, got %s", role, claims.Role)
	}

	// Verify token expiration is within 15 minutes
	expiresAt := claims.ExpiresAt.Time
	if expiresAt.Before(time.Now()) || expiresAt.After(time.Now().Add(16*time.Minute)) {
		t.Fatalf("Invalid expiration window: %v", expiresAt)
	}
}

func TestTokenHashIntegrity(t *testing.T) {
	tokenA := "sample_raw_refresh_token_string_123"
	tokenB := "sample_raw_refresh_token_string_123"
	tokenC := "different_token_string_456"

	hashA := core.HashToken(tokenA)
	hashB := core.HashToken(tokenB)
	hashC := core.HashToken(tokenC)

	if hashA != hashB {
		t.Fatal("Identical tokens must produce identical SHA-256 hashes")
	}

	if hashA == hashC {
		t.Fatal("Different tokens must produce different hashes")
	}
}
