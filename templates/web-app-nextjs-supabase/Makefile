# Aegis Forge — web-app-nextjs-supabase task runner
# Local Supabase requires the supabase CLI (`npm i -g supabase` or `npx supabase`).

.DEFAULT_GOAL := help

.PHONY: help first-run dev supabase-start supabase-stop migrate build typecheck audit clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

first-run: ## Install deps + start local Supabase + migrate + run dev server
	@if [ ! -f .env.local ]; then cp .env.example .env.local && echo "✔ .env.local created — run 'make supabase-start' and paste the printed anon key"; fi
	npm install
	$(MAKE) supabase-start
	$(MAKE) migrate
	npm run dev

dev: ## Run the Next.js dev server (Supabase must be running)
	npm run dev

supabase-start: ## Start the local Supabase stack (Docker)
	npx supabase start

supabase-stop: ## Stop the local Supabase stack
	npx supabase stop

migrate: ## Apply supabase/migrations to the local DB
	npx supabase db reset

build: ## Production build
	npm run build

typecheck: ## TypeScript check
	npm run typecheck

audit: ## Security audit (best-effort; needs gitleaks/semgrep/trivy)
	@gitleaks detect --source . --no-banner || true
	@semgrep --config p/owasp-top-ten --config p/typescript --error app lib || true
	@trivy fs --severity HIGH,CRITICAL . || true

clean: ## Remove build artifacts + stop supabase
	rm -rf .next node_modules
	npx supabase stop || true
