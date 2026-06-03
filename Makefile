.PHONY: install test test-cov lint format typecheck docker-test pre-commit clean

install:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=django_app_forge --cov-report=term-missing --cov-report=xml

lint:
	ruff check django_app_forge tests

format:
	ruff format django_app_forge tests
	ruff check --fix django_app_forge tests

typecheck:
	mypy django_app_forge

docker-test:
	docker build -f Dockerfile.test -t django-app-forge-test .
	docker run --rm django-app-forge-test

pre-commit:
	pre-commit run --all-files

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
