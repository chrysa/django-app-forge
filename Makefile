# makefile-tier: lib
.DEFAULT_GOAL := help

.PHONY: help install dev test test-cov lint format typecheck docker-test build pre-commit clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*##"}{printf "  %-20s %s\n", $$1, $$2}'

install: ## Install dev dependencies + pre-commit hooks
	pip install -e ".[dev]"
	pre-commit install

dev: install ## Alias for install (no separate dev server)

test: ## Run unit tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=django_app_forge --cov-report=term-missing --cov-report=xml

lint: ## Run ruff linter
	ruff check src/django_app_forge tests

format: ## Auto-format code
	ruff format src/django_app_forge tests
	ruff check --fix src/django_app_forge tests

typecheck: ## Run mypy type checking
	mypy src/django_app_forge

docker-test: ## Run tests in Docker (CI-compatible)
	docker build -f Dockerfile.test -t django-app-forge-test .
	docker run --rm django-app-forge-test

build: ## Build wheel distribution package
	python -m build

pre-commit: ## Run all pre-commit checks
	pre-commit run --all-files

clean: ## Remove build artifacts
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
