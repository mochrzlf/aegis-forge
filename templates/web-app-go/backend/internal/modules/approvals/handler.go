package approvals

import (
	"encoding/json"
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

type CreateApprovalRequest struct {
	ActionType string                 `json:"actionType"`
	Payload    map[string]interface{} `json:"payload"`
}

type ReviewApprovalRequest struct {
	Decision string `json:"decision"`
	Reason   string `json:"reason"`
}

func (h *Handler) Submit(w http.ResponseWriter, r *http.Request) {
	var req CreateApprovalRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.ActionType == "" {
		core.RespondError(w, http.StatusBadRequest, "VALIDATION_ERROR", "Action type is required", nil)
		return
	}

	currentUser := middleware.GetAuthUser(r)
	if currentUser == nil {
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Authentication required", nil)
		return
	}

	id, err := h.service.CreateRequest(r.Context(), currentUser.UserID, req.ActionType, req.Payload)
	if err != nil {
		core.RespondError(w, http.StatusInternalServerError, "INTERNAL_ERROR", "Failed to create approval request", nil)
		return
	}

	core.RespondSuccess(w, http.StatusCreated, map[string]interface{}{
		"id":     id,
		"status": "pending",
	}, nil)
}

func (h *Handler) Review(w http.ResponseWriter, r *http.Request) {
	requestID := chi.URLParam(r, "id")
	var req ReviewApprovalRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || (req.Decision != "approved" && req.Decision != "rejected") {
		core.RespondError(w, http.StatusBadRequest, "VALIDATION_ERROR", "Valid decision ('approved' or 'rejected') required", nil)
		return
	}

	currentUser := middleware.GetAuthUser(r)
	if currentUser == nil {
		core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Authentication required", nil)
		return
	}

	err := h.service.ReviewRequest(r.Context(), requestID, currentUser.UserID, req.Decision, req.Reason)
	if err != nil {
		if err.Error() == "MAKER_CANNOT_BE_CHECKER" {
			core.RespondError(w, http.StatusForbidden, "FORBIDDEN", "Maker-Checker violation: Maker cannot approve their own request (Four-Eyes Principle)", nil)
			return
		}
		if err.Error() == "NOT_FOUND" {
			core.RespondError(w, http.StatusNotFound, "NOT_FOUND", "Approval request not found", nil)
			return
		}
		if err.Error() == "ALREADY_RESOLVED" {
			core.RespondError(w, http.StatusBadRequest, "BAD_REQUEST", "Approval request is already resolved", nil)
			return
		}
		core.RespondError(w, http.StatusInternalServerError, "INTERNAL_ERROR", "Failed to review approval request", nil)
		return
	}

	core.RespondSuccess(w, http.StatusOK, map[string]interface{}{
		"id":     requestID,
		"status": req.Decision,
	}, nil)
}

func RegisterRoutes(r chi.Router, h *Handler, jwtSecret string) {
	r.Use(middleware.Authenticate(jwtSecret))

	r.Post("/", h.Submit)

	// Checker review requires admin/superadmin role
	r.Group(func(checkerGroup chi.Router) {
		checkerGroup.Use(middleware.AuthorizeRoles("admin", "superadmin"))
		checkerGroup.Post("/{id}/review", h.Review)
	})
}
