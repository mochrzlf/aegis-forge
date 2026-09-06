.DEFAULT_GOAL := help
SHELL := /usr/bin/env bash

# Colors for terminal output
BLUE    := \033[36m
GREEN   := \033[32m
YELLOW  := \033[33m
RED     := \033[31m
RESET   := \033[0m

.PHONY: help
help: ## Tampilkan panduan penggunaan perintah Makefile
	@echo -e "$(BLUE)==================================================================$(RESET)"
	@echo -e "$(BLUE)🚀 Universal Enterprise Baseline Task Runner$(RESET)"
	@echo -e "$(BLUE)==================================================================$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-16s$(RESET) %s\n", $$1, $$2}'
	@echo -e "$(BLUE)==================================================================$(RESET)"

.PHONY: audit
audit: ## Jalankan audit keamanan komprehensif (Git, .env, Private Keys, Gitleaks)
	@echo -e "$(YELLOW)🔍 Menjalankan Automated Security Audit...$(RESET)"
	@./scripts/devsec-check.sh

.PHONY: audit-staged
audit-staged: ## Jalankan audit khusus staged changes (seperti pre-commit)
	@echo -e "$(YELLOW)🔍 Menjalankan Gitleaks pre-commit staged audit...$(RESET)"
	@./scripts/devsec-check.sh --staged

.PHONY: mock-api
mock-api: ## Jalankan Prism Mock API server (port 4010) untuk testing Mobile & Frontend
	@echo -e "$(GREEN)🌐 Menjalankan Prism Mock API server pada port 4010...$(RESET)"
	@docker compose up -d prism

.PHONY: up
up: ## Jalankan stack lokal (PostgreSQL, Redis, Mailpit, Prism)
	@echo -e "$(GREEN)🚀 Menjalankan Docker Compose services...$(RESET)"
	@docker compose up -d

.PHONY: down
down: ## Hentikan seluruh stack Docker Compose
	@echo -e "$(YELLOW)🛑 Menghentikan Docker Compose services...$(RESET)"
	@docker compose down

.PHONY: status
status: ## Periksa status container Docker
	@docker compose ps

.PHONY: hermes
hermes: ## Buka Hermes AI Agent di terminal
	@command -v hermes >/dev/null 2>&1 && hermes || (~/.local/bin/hermes 2>/dev/null || echo "Hermes belum terpasang. Kunjungi https://hermes.sh untuk instalasi.")

.PHONY: hermes-ui
hermes-ui: ## Buka web dashboard Hermes di background (port 9119)
	@echo -e "$(GREEN)🌐 Membuka Hermes Web Dashboard di http://127.0.0.1:9119$(RESET)"
	@command -v hermes >/dev/null 2>&1 && hermes dashboard --no-open || (~/.local/bin/hermes dashboard --no-open 2>/dev/null || echo "Hermes belum terpasang.")

.PHONY: new
new: ## Buat proyek baru dari baseline (Penggunaan: make new NAME=NamaProyek PATH=/path/tujuan TYPE=web|mobile|trading|fullstack)
	@if [ -z "$(NAME)" ] || [ -z "$(PATH)" ]; then \
		echo -e "$(RED)❌ Gunakan: make new NAME=NamaProyek PATH=/path/tujuan [TYPE=web|mobile|trading|fullstack]$(RESET)"; \
		exit 1; \
	fi; \
	bash scripts/init-new-project.sh "$(NAME)" "$(PATH)" "$${TYPE:-fullstack}"
