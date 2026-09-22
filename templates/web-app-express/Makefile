.PHONY: help first-run up down restart logs test build clean

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
	@echo "🚀 Stack is running!"
	@echo "   API:      http://localhost:8000"
	@echo "   Mailpit:  http://localhost:8025"

up: ## Start the stack in background
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

logs: ## Tail api logs
	$(COMPOSE) logs -f api

test: ## Run unit tests (vitest)
	@cd backend && npm test

build: ## Build TypeScript backend
	@cd backend && npm run build

clean: ## Stop and remove volumes
	$(COMPOSE) down -v
