package auth

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
	"github.com/aegisforge/starter-go/internal/middleware"
	"github.com/go-chi/chi/v5"
)

type Handler struct {
	service *Service
}

func NewHandler(service *Service) *Handler {
	return &Handler{service: service}
}

type LoginRequest struct {
	Email    string `json:"email"`
	Password string `json:"password"`
}

func (h *Handler) Login(w http.ResponseWriter, r *http.Request) {
	var req LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		core.RespondError(w, http.StatusBadRequest, "VALIDATION_ERROR", "Invalid request payload", nil)
		return
	}

	if req.Email == "" || req.Password == "" {
		core.RespondError(w, http.StatusBadRequest, "VALIDATION_ERROR", "Email and password are required", nil)
		return
	}

	tokenPair, err := h.service.Authenticate(r.Context(), req.Email, req.Password)
	if err != nil {
		if err.Error() == "ACCOUNT_LOCKED" {
			core.RespondError(w, http.StatusLocked, "ACCOUNT_LOCKED", "Akun terkunci sementara akibat 5x kesalahan login berturut-turut. Silakan hubungi administrator atau coba 15 menit lagi.", nil)
			return
		}
		if err.Error() == "ACCOUNT_INACTIVE" {
			core.RespondError(w, http.StatusForbidden, "FORBIDDEN", "Akun Anda berstatus non-aktif atau ditangguhkan (JML Kill-Switch).", nil)
			return
		}
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Kredensial login tidak valid.", nil)
		return
	}

	// Set HttpOnly; Secure; SameSite=Strict cookie (AGENTS.md §4.1)
	http.SetCookie(w, &http.Cookie{
		Name:     "refreshToken",
		Value:    tokenPair.RefreshToken,
		Path:     "/api/auth",
		MaxAge:   7 * 24 * 3600,
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
	})

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"accessToken": tokenPair.AccessToken,
		"user": map[string]interface{}{
			"id":    tokenPair.User.ID,
			"email": tokenPair.User.Email,
			"role":  tokenPair.User.Role,
		},
	}, nil)
}

func (h *Handler) Refresh(w http.ResponseWriter, r *http.Request) {
	var rawToken string
	if cookie, err := r.Cookie("refreshToken"); err == nil {
		rawToken = cookie.Value
	} else if header := r.Header.Get("X-Refresh-Token"); header != "" {
		rawToken = header
	}

	if rawToken == "" {
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Missing refresh token cookie", nil)
		return
	}

	newAccess, newRefresh, err := h.service.Refresh(r.Context(), rawToken)
	if err != nil {
		if err.Error() == "TOKEN_REPLAY_DETECTED" {
			// Clear cookie immediately on replay attack
			http.SetCookie(w, &http.Cookie{
				Name:     "refreshToken",
				Value:    "",
				Path:     "/api/auth",
				MaxAge:   -1,
				HttpOnly: true,
				Secure:   true,
				SameSite: http.SameSiteStrictMode,
			})
			core.RespondError(w, http.StatusUnauthorized, "TOKEN_REVOKED", "Security violation: detected reuse of rotated refresh token. All sessions revoked.", nil)
			return
		}
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Invalid or expired refresh token", nil)
		return
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refreshToken",
		Value:    newRefresh,
		Path:     "/api/auth",
		MaxAge:   7 * 24 * 3600,
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
	})

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"accessToken": newAccess,
	}, nil)
}

func (h *Handler) Logout(w http.ResponseWriter, r *http.Request) {
	var rawToken string
	if cookie, err := r.Cookie("refreshToken"); err == nil {
		rawToken = cookie.Value
	}

	if rawToken != "" {
		_ = h.service.Logout(r.Context(), rawToken)
	}

	http.SetCookie(w, &http.Cookie{
		Name:     "refreshToken",
		Value:    "",
		Path:     "/api/auth",
		MaxAge:   -1,
		Expires:  time.Unix(0, 0),
		HttpOnly: true,
		Secure:   true,
		SameSite: http.SameSiteStrictMode,
	})

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"message": "Logged out successfully",
	}, nil)
}

func (h *Handler) Unlock(w http.ResponseWriter, r *http.Request) {
	var req struct {
		UserID string `json:"userId"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.UserID == "" {
		core.RespondError(w, http.StatusBadRequest, "VALIDATION_ERROR", "Valid userId required", nil)
		return
	}

	if err := h.service.Unlock(r.Context(), req.UserID); err != nil {
		core.RespondError(w, http.StatusInternalServerError, "INTERNAL_ERROR", "Failed to unlock account", nil)
		return
	}

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"message": "Account unlocked successfully",
		"userId":  req.UserID,
	}, nil)
}

func RegisterRoutes(r chi.Router, h *Handler, jwtSecret string) {
	r.Post("/login", h.Login)
	r.Post("/refresh", h.Refresh)
	r.Post("/logout", h.Logout)

	// Admin protected unlock endpoint
	r.Group(func(adminGroup chi.Router) {
		adminGroup.Use(middleware.Authenticate(jwtSecret))
		adminGroup.Use(middleware.AuthorizeRoles("admin", "superadmin"))
		adminGroup.Post("/unlock", h.Unlock)
	})
}
