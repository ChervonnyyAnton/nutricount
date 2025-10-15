# Nutrition Tracker Makefile
# Provides convenient commands for development and deployment

.PHONY: help install dev-install run test lint format security clean docker build deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Configuration
PYTHON := python3
PIP := pip3
DOCKER_IMAGE := nutrition-tracker
CONTAINER_NAME := nutrition-tracker-dev

help: ## Show this help message
	@echo "$(BLUE)Nutrition Tracker Development Commands$(RESET)"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(RESET)"
	@echo "  make install     # Install dependencies"
	@echo "  make run         # Start development server"
	@echo "  make test        # Run tests"

# === Installation ===

install: ## Install production dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

dev-install: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✅ Development dependencies installed$(RESET)"

dev-setup: dev-install ## Setup development environment
	@echo "$(BLUE)Setting up development environment...$(RESET)"
	mkdir -p data logs backups
	cp -n .env.example .env || true
	$(PYTHON) init_db.py
	@echo "$(GREEN)✅ Development environment ready$(RESET)"

# === Development ===

run: ## Start development server
	@echo "$(BLUE)Starting development server...$(RESET)"
	@echo "$(YELLOW)Access at: http://localhost:5000$(RESET)"
	FLASK_ENV=development FLASK_DEBUG=1 $(PYTHON) app.py

run-prod: ## Start production server locally
	@echo "$(BLUE)Starting production server...$(RESET)"
	gunicorn --config gunicorn.conf.py app:app

watch: ## Start development server with auto-reload
	@echo "$(BLUE)Starting development server with auto-reload...$(RESET)"
	@echo "$(YELLOW)Access at: http://localhost:5000$(RESET)"
	watchmedo auto-restart --patterns="*.py;*.html;*.css;*.js" --recursive $(PYTHON) app.py

# === Testing ===

test: ## Run test suite
	@echo "$(BLUE)Running tests...$(RESET)"
	pytest

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(RESET)"
	pytest-watch

test-fast: ## Run tests quickly (no coverage)
	@echo "$(BLUE)Running fast tests...$(RESET)"
	pytest --no-cov -x

test-coverage: ## Run tests with detailed coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	pytest --cov --cov-report=html --cov-report=term-missing
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(RESET)"

# === Code Quality ===

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	black app.py src/ tests/
	isort app.py src/ tests/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

format-check: ## Check if code is formatted correctly
	@echo "$(BLUE)Checking code format...$(RESET)"
	black --check app.py src/ tests/
	isort --check-only app.py src/ tests/

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(RESET)"
	flake8 app.py src/ tests/
	@echo "$(GREEN)✅ Linting passed$(RESET)"

type-check: ## Run type checking
	@echo "$(BLUE)Running type checks...$(RESET)"
	mypy app.py src/

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	bandit -r app.py src/
	safety check
	@echo "$(GREEN)✅ Security checks passed$(RESET)"

quality: format-check lint type-check security ## Run all quality checks

# === Database ===

db-init: ## Initialize database
	@echo "$(BLUE)Initializing database...$(RESET)"
	$(PYTHON) init_db.py
	@echo "$(GREEN)✅ Database initialized$(RESET)"

db-reset: ## Reset database (WARNING: destroys data)
	@echo "$(RED)⚠️  This will destroy all data!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	rm -f data/nutrition.db*
	$(PYTHON) init_db.py
	@echo "$(GREEN)✅ Database reset$(RESET)"

db-backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(RESET)"
	./scripts/backup.sh
	@echo "$(GREEN)✅ Backup created$(RESET)"

db-vacuum: ## Optimize database
	@echo "$(BLUE)Optimizing database...$(RESET)"
	sqlite3 data/nutrition.db "VACUUM;"
	@echo "$(GREEN)✅ Database optimized$(RESET)"

# === Docker ===

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)✅ Docker image built$(RESET)"

docker-build-prod: ## Build production Docker image
	@echo "$(BLUE)Building production Docker image...$(RESET)"
	docker build -f Dockerfile.production -t $(DOCKER_IMAGE):production .
	@echo "$(GREEN)✅ Production Docker image built$(RESET)"

docker-run: ## Run application in Docker
	@echo "$(BLUE)Running application in Docker...$(RESET)"
	docker run --rm -d \
		--name $(CONTAINER_NAME) \
		-p 5000:5000 \
		-v $(PWD)/data:/usr/src/app/data \
		$(DOCKER_IMAGE):latest
	@echo "$(GREEN)✅ Container started at http://localhost:5000$(RESET)"

docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker container...$(RESET)"
	docker stop $(CONTAINER_NAME) || true
	@echo "$(GREEN)✅ Container stopped$(RESET)"

docker-logs: ## Show Docker container logs
	docker logs -f $(CONTAINER_NAME)

docker-shell: ## Open shell in Docker container
	docker exec -it $(CONTAINER_NAME) /bin/bash

compose-up: ## Start with docker-compose
	@echo "$(BLUE)Starting with docker-compose...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✅ Services started$(RESET)"

compose-down: ## Stop docker-compose services
	@echo "$(BLUE)Stopping docker-compose services...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✅ Services stopped$(RESET)"

compose-logs: ## Show docker-compose logs
	docker-compose logs -f

# === Telegram ===

telegram-setup: ## Setup Telegram webhook
	@echo "$(BLUE)Setting up Telegram webhook...$(RESET)"
	./scripts/telegram-setup.sh
	@echo "$(GREEN)✅ Telegram webhook configured$(RESET)"

telegram-test: ## Test Telegram webhook
	@echo "$(BLUE)Testing Telegram webhook...$(RESET)"
	curl -X POST http://localhost:5000/telegram/webhook \
		-H "Content-Type: application/json" \
		-d '{"update_id": 1, "message": {"message_id": 1, "chat": {"id": 1}, "text": "/test"}}'

# === Deployment ===

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)Deploying to staging...$(RESET)"
	@echo "$(YELLOW)This will trigger GitHub Actions deployment$(RESET)"
	git push origin develop

deploy-prod: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(RESET)"
	@echo "$(RED)⚠️  This will deploy to production!$(RESET)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(YELLOW)Tag version and push to trigger deployment$(RESET)"
	@read -p "Enter version (e.g., v2.1.0): " version && \
	git tag $$version && \
	git push origin $$version

# === Monitoring ===

health: ## Check application health
	@echo "$(BLUE)Checking application health...$(RESET)"
	./scripts/healthcheck.sh
	@echo "$(GREEN)✅ Health check completed$(RESET)"

logs: ## Show application logs
	@echo "$(BLUE)Showing recent logs...$(RESET)"
	tail -f logs/*.log

monitor: ## Start monitoring dashboard
	@echo "$(BLUE)Starting monitoring...$(RESET)"
	docker-compose --profile monitoring up -d
	@echo "$(GREEN)✅ Monitoring started at http://localhost:3000$(RESET)"

# === Utilities ===

clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/ .tox/ .mypy_cache/ dist/ build/
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

update: ## Update dependencies
	@echo "$(BLUE)Updating dependencies...$(RESET)"
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies updated$(RESET)"

secrets-check: ## Validate required secrets
	@echo "$(BLUE)Checking secrets configuration...$(RESET)"
	./scripts/validate-secrets.sh

backup-auto: ## Create automated backup
	@echo "$(BLUE)Creating automated backup...$(RESET)"
	./scripts/backup.sh

# === Quick Commands ===

quickstart: ## Complete quickstart setup
	@echo "$(BLUE)🥗 Nutrition Tracker - Complete Setup$(RESET)"
	./scripts/quickstart.sh

dev: dev-setup run ## Setup and run development environment

all-checks: format-check lint type-check security test ## Run all quality checks

ci: all-checks ## Run CI pipeline locally

# === Information ===

info: ## Show project information
	@echo "$(BLUE)Nutrition Tracker Project Information$(RESET)"
	@echo "===================================="
	@echo "Python version: $$($(PYTHON) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Docker version: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Project size: $$(du -sh . | cut -f1)"
	@echo "Database size: $$([ -f data/nutrition.db ] && du -h data/nutrition.db | cut -f1 || echo 'Not created')"
	@echo "Log files: $$(ls -la logs/ 2>/dev/null | wc -l || echo '0') files"
	@echo "Backup files: $$(ls -la backups/ 2>/dev/null | wc -l || echo '0') files"

status: ## Show application status
	@echo "$(BLUE)Application Status$(RESET)"
	@echo "=================="
	@echo "Health: $$(curl -s http://localhost:5000/health | jq -r '.status' 2>/dev/null || echo 'Not running')"
	@echo "Containers: $$(docker ps --filter name=nutrition --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null || echo 'None')"

version: ## Show version information
	@echo "$(BLUE)Version Information$(RESET)"
	@echo "==================="
	@echo "Application: $$(grep VERSION src/config.py | cut -d'"' -f2)"
	@echo "Git commit: $$(git rev-parse --short HEAD 2>/dev/null || echo 'Unknown')"
	@echo "Git branch: $$(git branch --show-current 2>/dev/null || echo 'Unknown')"

# === Advanced ===

profile: ## Profile application performance
	@echo "$(BLUE)Profiling application...$(RESET)"
	$(PYTHON) -m cProfile -o profile.stats app.py
	@echo "$(GREEN)✅ Profile saved to profile.stats$(RESET)"

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running benchmarks...$(RESET)"
	locust --headless --users 10 --spawn-rate 2 --run-time 30s --host http://localhost:5000

load-test: ## Run load tests
	@echo "$(BLUE)Running load tests...$(RESET)"
	@echo "$(YELLOW)Make sure application is running first$(RESET)"
	ab -n 1000 -c 10 http://localhost:5000/health

stress-test: ## Run stress tests
	@echo "$(BLUE)Running stress tests...$(RESET)"
	@echo "$(RED)⚠️  This will put heavy load on the application$(RESET)"
	ab -n 10000 -c 100 http://localhost:5000/api/products

# === Backup & Restore ===

backup-full: ## Create full system backup
	@echo "$(BLUE)Creating full system backup...$(RESET)"
	mkdir -p backups/full-$(shell date +%Y%m%d_%H%M%S)
	cp -r data/ backups/full-$(shell date +%Y%m%d_%H%M%S)/
	cp -r logs/ backups/full-$(shell date +%Y%m%d_%H%M%S)/
	tar -czf backups/full-$(shell date +%Y%m%d_%H%M%S).tar.gz backups/full-$(shell date +%Y%m%d_%H%M%S)/
	rm -rf backups/full-$(shell date +%Y%m%d_%H%M%S)/
	@echo "$(GREEN)✅ Full backup created$(RESET)"

restore: ## Restore from backup (interactive)
	@echo "$(BLUE)Available backups:$(RESET)"
	@ls -la backups/
	@read -p "Enter backup filename: " backup && \
	echo "$(RED)⚠️  This will overwrite current data!$(RESET)" && \
	read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] && \
	cp backups/$$backup data/nutrition.db && \
	echo "$(GREEN)✅ Restored from $$backup$(RESET)"

# Show help by default
.DEFAULT: help
