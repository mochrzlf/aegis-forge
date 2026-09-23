package config

import (
	"os"
)

type Config struct {
	Port             string
	DatabaseURL      string
	RedisURL         string
	JWTAccessSecret  string
	JWTRefreshSecret string
	Environment      string
	CORSOrigin       string
}

func LoadConfig() *Config {
	return &Config{
		Port:             getEnv("PORT", "8000"),
		DatabaseURL:      getEnv("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/aegis_forge_dev?sslmode=disable"),
		RedisURL:         getEnv("REDIS_URL", "redis://localhost:6379/0"),
		JWTAccessSecret:  getEnv("JWT_ACCESS_SECRET", "dev_access_secret_do_not_use_in_prod_replace_me_32chars!"),
		JWTRefreshSecret: getEnv("JWT_REFRESH_SECRET", "dev_refresh_secret_do_not_use_in_prod_replace_me_32chars!"),
		Environment:      getEnv("ENVIRONMENT", "development"),
		CORSOrigin:       getEnv("CORS_ORIGIN", "http://localhost:3000"),
	}
}

func getEnv(key, fallback string) string {
	if val := os.Getenv(key); val != "" {
		return val
	}
	return fallback
}
