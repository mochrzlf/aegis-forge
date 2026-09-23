package health

import (
	"database/sql"
	"net/http"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
	"github.com/go-chi/chi/v5"
	"github.com/redis/go-redis/v9"
)

type Handler struct {
	db  *sql.DB
	rdb *redis.Client
}

func NewHandler(db *sql.DB, rdb *redis.Client) *Handler {
	return &Handler{db: db, rdb: rdb}
}

func (h *Handler) Live(w http.ResponseWriter, r *http.Request) {
	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"status":    "ok",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}, nil)
}

func (h *Handler) Ready(w http.ResponseWriter, r *http.Request) {
	dbStatus := "connected"
	if h.db != nil {
		if err := h.db.Ping(); err != nil {
			dbStatus = "disconnected"
		}
	} else {
		dbStatus = "skipped"
	}

	redisStatus := "connected"
	if h.rdb != nil {
		if err := h.rdb.Ping(r.Context()).Err(); err != nil {
			redisStatus = "disconnected"
		}
	} else {
		redisStatus = "skipped"
	}

	isHealthy := dbStatus != "disconnected" && redisStatus != "disconnected"
	status := http.StatusOK
	if !isHealthy {
		status = http.StatusServiceUnavailable
	}

	core.RespondSuccess(w, status, map[string]interface{}{
		"status":    "ready",
		"database":  dbStatus,
		"redis":     redisStatus,
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	}, nil)
}

func RegisterRoutes(r chi.Router, h *Handler) {
	r.Get("/live", h.Live)
	r.Get("/ready", h.Ready)
}
