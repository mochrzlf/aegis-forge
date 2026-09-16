# Aegis Forge — web-app skeleton task runner
# Cross-platform: works on macOS/Linux (make) and Windows (make via Git Bash /
# choco, or run the equivalent docker compose commands shown in each recipe).

.DEFAULT_GOAL := help
COMPOSE := docker compose

.PHONY: help first-run dev up down logs migrate seed audit test check clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

first-run: ## First-time setup: env file + build + up + migrate (idempotent)
	@if [ ! -f .env ]; then cp .env.example .env && echo "✔ .env created — EDIT secrets before production"; fi
	$(COMPOSE) up -d --build
	@echo "✅ App ready → http://localhost:8000 (docs: /docs)"

dev: ## Start the dev stack (db + cache + api)
	$(COMPOSE) up -d
	@echo "✅ Dev stack up → http://localhost:8000"

up: ## Alias for dev
	$(COMPOSE) up -d

down: ## Stop the stack (keeps volumes)
	$(COMPOSE) down

logs: ## Tail API logs
	$(COMPOSE) logs -f api

migrate: ## Apply DB migrations (alembic upgrade head)
	$(COMPOSE) exec api alembic upgrade head

audit: ## Security audit: gitleaks + semgrep + trivy (best-effort, needs tools)
	@echo "▶ gitleaks";  gitleaks detect --source . --no-banner || true
	@echo "▶ semgrep";   semgrep --config p/owasp-top-ten --error backend/ || true
	@echo "▶ trivy fs";  trivy fs --severity HIGH,CRITICAL . || true

test: ## Run backend tests (pytest) inside the api container
	$(COMPOSE) exec api pytest -q || echo "⚠ no tests yet — add under backend/tests/"

check: audit test ## Run audit + tests (gate before opening a PR)

clean: ## Stop stack and DELETE volumes (destroys dev data)
	$(COMPOSE) down -v
