package users

import (
	"net/http"

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

func (h *Handler) Suspend(w http.ResponseWriter, r *http.Request) {
	targetID := chi.URLParam(r, "id")
	currentUser := middleware.GetAuthUser(r)

	if currentUser == nil {
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Authentication required", nil)
		return
	}

	revokedCount, err := h.service.SuspendUser(r.Context(), targetID, currentUser.UserID)
	if err != nil {
		if err.Error() == "CANNOT_SUSPEND_SELF" {
			core.RespondError(w, http.StatusBadRequest, "BAD_REQUEST", "Admin cannot suspend their own account", nil)
			return
		}
		if err.Error() == "USER_NOT_FOUND" {
			core.RespondError(w, http.StatusNotFound, "NOT_FOUND", "User not found", nil)
			return
		}
		core.RespondError(w, http.StatusInternalServerError, "INTERNAL_ERROR", "Failed to suspend user", nil)
		return
	}

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"userId":          targetID,
		"status":          "suspended",
		"sessionsRevoked": revokedCount,
	}, nil)
}

func (h *Handler) GetProfile(w http.ResponseWriter, r *http.Request) {
	targetID := chi.URLParam(r, "id")
	currentUser := middleware.GetAuthUser(r)

	if currentUser == nil {
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Authentication required", nil)
		return
	}

	user, err := h.service.GetUser(r.Context(), targetID, currentUser.UserID, currentUser.Role)
	if err != nil {
		if err.Error() == "FORBIDDEN" {
			core.RespondError(w, http.StatusForbidden, "FORBIDDEN", "Forbidden: You cannot access other users profiles (Anti-IDOR)", nil)
			return
		}
		if err.Error() == "NOT_FOUND" {
			core.RespondError(w, http.StatusNotFound, "NOT_FOUND", "User not found", nil)
			return
		}
		core.RespondError(w, http.StatusInternalServerError, "INTERNAL_ERROR", "Failed to fetch user", nil)
		return
	}

	core.RespondSuccess(w, http.StatusOK, user, nil)
}

func RegisterRoutes(r chi.Router, h *Handler, jwtSecret string) {
	r.Use(middleware.Authenticate(jwtSecret))

	r.Get("/{id}", h.GetProfile)

	// Admin-only operations
	r.Group(func(adminGroup chi.Router) {
		adminGroup.Use(middleware.AuthorizeRoles("admin", "superadmin"))
		adminGroup.Put("/{id}/suspend", h.Suspend)
	})
}
