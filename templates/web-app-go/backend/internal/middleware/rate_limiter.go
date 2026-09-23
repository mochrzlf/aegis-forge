package middleware

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"strings"
	"sync"
	"time"

	"github.com/aegisforge/starter-go/internal/core"
	"github.com/redis/go-redis/v9"
)

type InMemoryLimiter struct {
	mu      sync.Mutex
	records map[string][]time.Time
}

var memoryLimiter = &InMemoryLimiter{
	records: make(map[string][]time.Time),
}

func (m *InMemoryLimiter) Allow(key string, limit int, window time.Duration) bool {
	m.mu.Lock()
	defer m.mu.Unlock()

	now := time.Now()
	threshold := now.Add(-window)

	timestamps := m.records[key]
	var valid []time.Time
	for _, t := range timestamps {
		if t.After(threshold) {
			valid = append(valid, t)
		}
	}

	if len(valid) >= limit {
		m.records[key] = valid
		return false
	}

	valid = append(valid, now)
	m.records[key] = valid
	return true
}

func RateLimiter(rdb *redis.Client, limit int, window time.Duration) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			clientIP := getClientIP(r)
			key := fmt.Sprintf("rl:%s:%s", r.URL.Path, clientIP)

			var allowed bool
			if rdb != nil {
				ctx := context.Background()
				now := time.Now().UnixNano()
				windowStart := now - window.Nanoseconds()

				pipe := rdb.Pipeline()
				pipe.ZRemRangeByScore(ctx, key, "0", fmt.Sprintf("%d", windowStart))
				pipe.ZAdd(ctx, key, redis.Z{Score: float64(now), Member: fmt.Sprintf("%d", now)})
				pipe.ZCard(ctx, key)
				pipe.Expire(ctx, key, window)

				cmds, err := pipe.Exec(ctx)
				if err == nil && len(cmds) >= 3 {
					count := cmds[2].(*redis.IntCmd).Val()
					allowed = count <= int64(limit)
				} else {
					// Fallback to in-memory if Redis error
					allowed = memoryLimiter.Allow(key, limit, window)
				}
			} else {
				allowed = memoryLimiter.Allow(key, limit, window)
			}

			if !allowed {
				core.RespondError(w, http.StatusTooManyRequests, "RATE_LIMIT_EXCEEDED", "Too many requests. Please slow down.", nil)
				return
			}

			next.ServeHTTP(w, r)
		})
	}
}

func getClientIP(r *http.Request) string {
	forwarded := r.Header.Get("X-Forwarded-For")
	if forwarded != "" {
		parts := strings.Split(forwarded, ",")
		return strings.TrimSpace(parts[0])
	}
	ip, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return ip
}
