# Travel AI Assistant - Makefile

.PHONY: help install run test docker-build docker-up docker-down docker-logs clean

help: ## Show this help message
	@echo "Travel AI Assistant - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

run: ## Run development server
	@echo "🚀 Starting development server..."
	uvicorn app.main:app --reload --port 8000

test: ## Run tests
	@echo "🧪 Running tests..."
	pytest -v

test-cov: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linting
	@echo "🔍 Running linters..."
	black app/ tests/
	flake8 app/ tests/
	mypy app/

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker-compose build

docker-up: ## Start Docker containers
	@echo "🐳 Starting Docker containers..."
	docker-compose up -d

docker-down: ## Stop Docker containers
	@echo "🐳 Stopping Docker containers..."
	docker-compose down

docker-logs: ## View Docker logs
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

docker-restart: docker-down docker-up ## Restart Docker containers

docker-shell: ## Open shell in backend container
	@echo "🐚 Opening shell in backend container..."
	docker-compose exec backend /bin/bash

db-migrate: ## Run database migrations
	@echo "🗄️  Running database migrations..."
	# Add migration command here

clean: ## Clean up cache and temporary files
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	rm -rf dist/ build/ htmlcov/

dev-setup: ## Complete development setup
	@echo "🛠️  Setting up development environment..."
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env with your API keys!"; \
	fi
	@if [ ! -d venv ]; then \
		echo "🐍 Creating virtual environment..."; \
		python3 -m venv venv; \
		echo "✅ Virtual environment created. Activate with: source venv/bin/activate"; \
	fi
	@echo "📦 Installing dependencies..."
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Development setup complete!"

format: ## Format code
	@echo "✨ Formatting code..."
	black app/ tests/
	isort app/ tests/

check: lint test ## Run all checks (lint + test)

.DEFAULT_GOAL := help
