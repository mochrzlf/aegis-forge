package tests

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/aegisforge/starter-go/internal/middleware"
)

func TestRateLimiter(t *testing.T) {
	// 5 requests allowed per 500ms
	handler := middleware.RateLimiter(nil, 5, 500*time.Millisecond)(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("OK"))
	}))

	// Send 5 allowed requests
	for i := 1; i <= 5; i++ {
		req := httptest.NewRequest("GET", "/test-rl", nil)
		req.RemoteAddr = "192.168.1.50:1234"
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Fatalf("Request %d expected 200 OK, got %d", i, w.Code)
		}
	}

	// 6th request must be blocked (HTTP 429)
	req := httptest.NewRequest("GET", "/test-rl", nil)
	req.RemoteAddr = "192.168.1.50:1234"
	w := httptest.NewRecorder()
	handler.ServeHTTP(w, req)

	if w.Code != http.StatusTooManyRequests {
		t.Fatalf("6th request expected 429 Too Many Requests, got %d", w.Code)
	}

	// Another IP address must still be allowed (IP isolation)
	reqIsolated := httptest.NewRequest("GET", "/test-rl", nil)
	reqIsolated.RemoteAddr = "192.168.1.99:1234"
	wIsolated := httptest.NewRecorder()
	handler.ServeHTTP(wIsolated, reqIsolated)

	if wIsolated.Code != http.StatusOK {
		t.Fatalf("Isolated IP expected 200 OK, got %d", wIsolated.Code)
	}
}
