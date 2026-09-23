package main

import (
	"context"
	"fmt"
	"log"
	"os"

	"github.com/aegisforge/starter-go/internal/config"
	"github.com/aegisforge/starter-go/internal/core"
)

func main() {
	cfg := config.LoadConfig()

	adminEmail := getEnv("SEED_ADMIN_EMAIL", "superadmin@aegisforge.dev")
	adminPassword := getEnv("SEED_ADMIN_PASSWORD", "SuperAdmin@Aegis123!")

	checkerEmail := getEnv("SEED_CHECKER_EMAIL", "checker@aegisforge.dev")
	checkerPassword := getEnv("SEED_CHECKER_PASSWORD", "CheckerAdmin@Aegis123!")

	db, err := core.InitDB(cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("❌ Database connection failed: %v", err)
	}
	defer db.Close()

	ctx := context.Background()

	fmt.Println("🌱 Seeding administrative users for Aegis Forge (Go)...")

	// 1. Superadmin (Maker / Root Admin)
	var existingAdminID string
	err = db.QueryRowContext(ctx, "SELECT id FROM users WHERE email = $1", adminEmail).Scan(&existingAdminID)
	if err != nil {
		pwdHash, _ := core.HashPassword(adminPassword)
		var newID string
		err = db.QueryRowContext(ctx,
			`INSERT INTO users (email, password_hash, role, status, created_at, updated_at)
			 VALUES ($1, $2, 'superadmin', 'active', NOW(), NOW())
			 RETURNING id`, adminEmail, pwdHash).Scan(&newID)
		if err != nil {
			log.Fatalf("Failed to create superadmin: %v", err)
		}
		fmt.Printf("  ✅ Created Superadmin: %s (Role: superadmin)\n", adminEmail)
	} else {
		fmt.Printf("  ℹ️ Superadmin already exists: %s\n", adminEmail)
	}

	// 2. Checker (Reviewer / Approver)
	var existingCheckerID string
	err = db.QueryRowContext(ctx, "SELECT id FROM users WHERE email = $1", checkerEmail).Scan(&existingCheckerID)
	if err != nil {
		pwdHash, _ := core.HashPassword(checkerPassword)
		var newID string
		err = db.QueryRowContext(ctx,
			`INSERT INTO users (email, password_hash, role, status, created_at, updated_at)
			 VALUES ($1, $2, 'admin', 'active', NOW(), NOW())
			 RETURNING id`, checkerEmail, pwdHash).Scan(&newID)
		if err != nil {
			log.Fatalf("Failed to create checker: %v", err)
		}
		fmt.Printf("  ✅ Created Checker: %s (Role: admin)\n", checkerEmail)
	} else {
		fmt.Printf("  ℹ️ Checker already exists: %s\n", checkerEmail)
	}

	fmt.Println("\n✨ Seeding completed successfully.")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Println("🔑 INITIAL CREDENTIALS (DEV ONLY):")
	fmt.Printf("   • Superadmin : %s | %s\n", adminEmail, adminPassword)
	fmt.Printf("   • Checker    : %s | %s\n", checkerEmail, checkerPassword)
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
}

func getEnv(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}
