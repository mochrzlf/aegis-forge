package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/aegisforge/starter-go/internal/config"
	"github.com/aegisforge/starter-go/internal/core"
	"github.com/aegisforge/starter-go/internal/middleware"
	"github.com/aegisforge/starter-go/internal/modules/approvals"
	"github.com/aegisforge/starter-go/internal/modules/auth"
	"github.com/aegisforge/starter-go/internal/modules/health"
	"github.com/aegisforge/starter-go/internal/modules/users"
	"github.com/go-chi/chi/v5"
	chiMiddleware "github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func main() {
	cfg := config.LoadConfig()

	log.Println("🚀 Starting Aegis Forge Go Backend...")

	// 1. Initialize Database
	db, err := core.InitDB(cfg.DatabaseURL)
	if err != nil {
		log.Printf("⚠️ PostgreSQL connection failed: %v (continuing with degraded state)", err)
	} else {
		defer db.Close()
		log.Println("✅ PostgreSQL connected successfully.")
	}

	// 2. Initialize Redis Cache
	rdb, err := core.InitRedis(cfg.RedisURL)
	if err != nil {
		log.Printf("⚠️ Redis connection failed: %v (continuing with in-memory limiter)", err)
	} else {
		defer rdb.Close()
		log.Println("✅ Redis connected successfully.")
	}

	// 3. Router & Global Middlewares
	r := chi.NewRouter()

	r.Use(chiMiddleware.RequestID)
	r.Use(chiMiddleware.RealIP)
	r.Use(chiMiddleware.Logger)
	r.Use(chiMiddleware.Recoverer)
	r.Use(middleware.SecurityHeaders)

	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{cfg.CORSOrigin},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-Refresh-Token"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	// Global rate limiter: 100 req / minute
	r.Use(middleware.RateLimiter(rdb, 100, 1*time.Minute))

	// 4. Initialize Services & Handlers
	healthHandler := health.NewHandler(db, rdb)
	authService := auth.NewService(db, cfg.JWTAccessSecret, cfg.JWTRefreshSecret)
	authHandler := auth.NewHandler(authService)
	userService := users.NewService(db)
	userHandler := users.NewHandler(userService)
	approvalService := approvals.NewService(db)
	approvalHandler := approvals.NewHandler(approvalService)

	// 5. Mount Routes
	r.Route("/health", func(hr chi.Router) {
		health.RegisterRoutes(hr, healthHandler)
	})

	r.Route("/api/auth", func(ar chi.Router) {
		auth.RegisterRoutes(ar, authHandler, cfg.JWTAccessSecret)
	})

	r.Route("/api/users", func(ur chi.Router) {
		users.RegisterRoutes(ur, userHandler, cfg.JWTAccessSecret)
	})

	r.Route("/api/approvals", func(apr chi.Router) {
		approvals.RegisterRoutes(apr, approvalHandler, cfg.JWTAccessSecret)
	})

	// 6. Graceful Server Listen
	server := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      r,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	go func() {
		log.Printf("🌐 Server listening on http://localhost:%s\n", cfg.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("Server error: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("🛑 Shutting down server...")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server forced to shutdown: %v", err)
	}

	fmt.Println("👋 Server exited cleanly.")
}
