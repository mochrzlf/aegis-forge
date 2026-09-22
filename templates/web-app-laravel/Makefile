.PHONY: help first-run up down restart logs test migrate clean

COMPOSE ?= docker compose

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

first-run: ## Setup and run the stack from scratch
	@if [ ! -f backend/.env ]; then \
		echo "📋 Copying backend/.env.example to backend/.env..."; \
		cp backend/.env.example backend/.env; \
	fi
	$(COMPOSE) up -d --build
	@echo "⏳ Waiting for database and running migrations..."
	@sleep 3
	$(COMPOSE) exec api php artisan migrate --force
	@echo ""
	@echo "🚀 Laravel Stack is running!"
	@echo "   API:      http://localhost:8000"
	@echo "   Mailpit:  http://localhost:8025"

up: ## Start the stack in background
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

logs: ## Tail api and web logs
	$(COMPOSE) logs -f

test: ## Run unit and feature tests
	@cd backend && php artisan test

migrate: ## Run database migrations
	$(COMPOSE) exec api php artisan migrate

clean: ## Stop and remove volumes
	$(COMPOSE) down -v
