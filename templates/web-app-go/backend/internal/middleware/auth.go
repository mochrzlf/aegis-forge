package middleware

import (
	"context"
	"net/http"
	"strings"

	"github.com/aegisforge/starter-go/internal/core"
)

type contextKey string

const (
	UserContextKey contextKey = "authUser"
)

type AuthUser struct {
	UserID string
	Role   string
}

func GetAuthUser(r *http.Request) *AuthUser {
	if val := r.Context().Value(UserContextKey); val != nil {
		if user, ok := val.(*AuthUser); ok {
			return user
		}
	}
	return nil
}

func Authenticate(jwtSecret string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" || !strings.HasPrefix(authHeader, "Bearer ") {
				core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Missing or invalid Authorization header", nil)
				return
			}

			tokenStr := strings.TrimPrefix(authHeader, "Bearer ")
			claims, err := core.VerifyJWT(tokenStr, jwtSecret)
			if err != nil {
				core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Invalid or expired access token", nil)
				return
			}

			user := &AuthUser{
				UserID: claims.UserID,
				Role:   claims.Role,
			}

			ctx := context.WithValue(r.Context(), UserContextKey, user)
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

func AuthorizeRoles(roles ...string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			user := GetAuthUser(r)
			if user == nil {
				core.RespondError(w, http.StatusUnauthorized, "UNAUTHORIZED", "Authentication required", nil)
				return
			}

			hasRole := false
			for _, role := range roles {
				if user.Role == role {
					hasRole = true
					break
				}
			}

			if !hasRole {
				core.RespondError(w, http.StatusForbidden, "FORBIDDEN", "Insufficient role privileges", nil)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}
