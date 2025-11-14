.PHONY: help install install-dev setup clean test lint format type-check run docker-up docker-down docker-logs

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Scam Detection Platform - Make Commands"
	@echo "========================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install production dependencies
	pip install -e .
	python -m spacy download en_core_web_sm

install-dev: ## Install development dependencies
	pip install -e ".[dev]"
	python -m spacy download en_core_web_sm
	pre-commit install

setup: ## Run initial setup script
	python scripts/setup.py

# Cleaning
clean: ## Remove build artifacts and cache files
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/
	rm -rf .pytest_cache/ .mypy_cache/ .coverage htmlcov/
	rm -rf logs/*.log

# Testing
test: ## Run tests with coverage
	pytest --cov=src --cov-report=term-missing --cov-report=html -v

test-quick: ## Run tests without coverage
	pytest -v

test-watch: ## Run tests in watch mode
	pytest-watch

# Code Quality
lint: ## Run linters
	flake8 src/ tests/
	pylint src/

format: ## Format code with black and isort
	black src/ tests/
	isort src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/
	isort --check-only src/ tests/

type-check: ## Run type checking with mypy
	mypy src/

check: format-check type-check lint test ## Run all checks

# Development
run: ## Run development server
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Run production server
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4

notebook: ## Start Jupyter notebook
	jupyter notebook

# Docker
docker-build: ## Build Docker image
	docker build -t scam-detector:latest .

docker-up: ## Start Docker services
	docker-compose up -d

docker-down: ## Stop Docker services
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-shell: ## Open shell in API container
	docker-compose exec api /bin/bash

docker-clean: ## Remove Docker containers and volumes
	docker-compose down -v
	docker system prune -f

# Database
db-migrate: ## Run database migrations
	alembic upgrade head

db-rollback: ## Rollback last migration
	alembic downgrade -1

db-reset: ## Reset database (WARNING: deletes all data)
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	make db-migrate

# Pre-commit
pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# Documentation
docs: ## Generate documentation
	@echo "Documentation generation not yet implemented"

# Monitoring
metrics: ## View Prometheus metrics
	@echo "Opening Prometheus at http://localhost:9090"
	open http://localhost:9090 || xdg-open http://localhost:9090

# Utilities
env: ## Create .env file from template
	cp .env.example .env
	@echo ".env file created. Please update with your configuration."

download-models: ## Download pre-trained models
	@echo "Downloading pre-trained models..."
	python -m spacy download en_core_web_sm
	@echo "Models downloaded successfully"

check-deps: ## Check for outdated dependencies
	pip list --outdated

update-deps: ## Update dependencies (use with caution)
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

# Performance
profile: ## Profile API performance
	python -m cProfile -o profile.stats src/api/main.py

benchmark: ## Run performance benchmarks
	@echo "Benchmarking not yet implemented"

# Security
security-check: ## Run security checks
	pip-audit
	bandit -r src/

# Git
commit: check ## Run checks before committing
	@echo "All checks passed. Ready to commit."

push: check ## Run checks before pushing
	@echo "All checks passed. Ready to push."
	git push

# Release
version: ## Show current version
	@python -c "from src import __version__; print(f'Version: {__version__}')"

# Quick commands
dev: install-dev docker-up ## Setup development environment
prod: install docker-build ## Setup production environment
