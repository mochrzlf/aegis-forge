.DEFAULT_GOAL := help
SHELL := /usr/bin/env bash

# Colors for terminal output
BLUE    := \033[36m
GREEN   := \033[32m
YELLOW  := \033[33m
RED     := \033[31m
RESET   := \033[0m

.PHONY: help
help: ## Display Makefile usage guide
	@echo -e "$(BLUE)==================================================================$(RESET)"
	@echo -e "$(BLUE)🚀 Universal Aegis Forge Task Runner$(RESET)"
	@echo -e "$(BLUE)==================================================================$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-16s$(RESET) %s\n", $$1, $$2}'
	@echo -e "$(BLUE)==================================================================$(RESET)"

.PHONY: audit
audit: ## Run comprehensive security audit (Git, .env, Private Keys, Gitleaks)
	@echo -e "$(YELLOW)🔍 Running Automated Security Audit...$(RESET)"
	@./scripts/devsec-check.sh

.PHONY: audit-staged
audit-staged: ## Run audit specifically for staged changes (as in pre-commit)
	@echo -e "$(YELLOW)🔍 Running Gitleaks pre-commit staged audit...$(RESET)"
	@./scripts/devsec-check.sh --staged

.PHONY: mock-api
mock-api: ## Start Prism Mock API server (port 4010) for Mobile & Frontend testing
	@echo -e "$(GREEN)🌐 Starting Prism Mock API server on port 4010...$(RESET)"
	@docker compose up -d prism

.PHONY: up
up: ## Start local services stack (PostgreSQL, Redis, Mailpit, Prism)
	@echo -e "$(GREEN)🚀 Starting Docker Compose services...$(RESET)"
	@docker compose up -d

.PHONY: down
down: ## Stop entire Docker Compose stack
	@echo -e "$(YELLOW)🛑 Stopping Docker Compose services...$(RESET)"
	@docker compose down

.PHONY: status
status: ## Check Docker container status
	@docker compose ps

.PHONY: hermes
hermes: ## Open Hermes AI Agent in terminal
	@command -v hermes >/dev/null 2>&1 && hermes || (~/.local/bin/hermes 2>/dev/null || echo "Hermes is not installed. Visit https://hermes.sh for installation instructions.")

.PHONY: hermes-ui
hermes-ui: ## Launch Hermes Web Dashboard in background (port 9119)
	@echo -e "$(GREEN)🌐 Launching Hermes Web Dashboard at http://127.0.0.1:9119$(RESET)"
	@command -v hermes >/dev/null 2>&1 && hermes dashboard --no-open || (~/.local/bin/hermes dashboard --no-open 2>/dev/null || echo "Hermes is not installed.")

.PHONY: new
new: ## Create new project from baseline (Usage: make new NAME=ProjectName PATH=/target/path TYPE=web|mobile|trading|fullstack)
	@if [ -z "$(NAME)" ] || [ -z "$(PATH)" ]; then \
		echo -e "$(RED)❌ Usage: make new NAME=ProjectName PATH=/target/path [TYPE=web|mobile|trading|fullstack]$(RESET)"; \
		exit 1; \
	fi; \
	bash scripts/init-new-project.sh "$(NAME)" "$(PATH)" "$${TYPE:-fullstack}"
