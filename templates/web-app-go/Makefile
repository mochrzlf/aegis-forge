.PHONY: help first-run up down restart logs test build seed clean

COMPOSE ?= docker compose

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

first-run: ## Setup and run the stack from scratch
	@if [ ! -f .env ]; then \
		echo "📋 Copying .env.example to .env..."; \
		cp .env.example .env; \
	fi
	$(COMPOSE) up -d --build
	@echo ""
	@echo "🚀 Go Stack is running!"
	@echo "   API:      http://localhost:8000"
	@echo "   Health:   http://localhost:8000/health/live"

seed: ## Seed initial administrative users (Superadmin & Checker)
	@if command -v go >/dev/null 2>&1; then \
		cd backend && go run ./cmd/seed; \
	else \
		$(COMPOSE) exec api /app/seed; \
	fi

up: ## Start the stack in background
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

logs: ## Tail api logs
	$(COMPOSE) logs -f api

test: ## Run unit tests
	@cd backend && go test -v ./...

build: ## Build Go binary locally
	@cd backend && go build -o bin/server ./cmd/server

clean: ## Stop and remove volumes
	$(COMPOSE) down -v
