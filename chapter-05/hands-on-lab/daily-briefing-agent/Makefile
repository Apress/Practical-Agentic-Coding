# Daily Briefing Agent - Makefile
# Common development tasks and commands

.PHONY: help install dev test test-unit test-integration test-coverage lint format clean

# Default target
help:
	@echo "Daily Briefing Agent - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make dev            Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-integration  Run integration tests (requires LocalStack)"
	@echo "  make test-coverage  Run tests with coverage report"
	@echo "  make test-browser   Run browser tests (requires Playwright)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linting checks"
	@echo "  make format         Format code with black and isort"
	@echo "  make check          Run all quality checks"
	@echo ""
	@echo "Development:"
	@echo "  make run            Start development server"
	@echo "  make localstack     Start LocalStack services"
	@echo "  make clean          Remove generated files"

# ===========================================
# Setup
# ===========================================

install:
	pip install -r requirements.txt

dev: install
	pip install black isort flake8 mypy pytest-cov hypothesis playwright
	playwright install chromium

# ===========================================
# Testing
# ===========================================

test:
	pytest

test-unit:
	pytest -m unit -v

test-integration:
	pytest -m integration -v

test-property:
	pytest -m property -v

test-browser:
	pytest -m browser -v

test-coverage:
	pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# ===========================================
# Code Quality
# ===========================================

lint:
	flake8 src tests --max-line-length=100
	mypy src --ignore-missing-imports

format:
	black src tests --line-length=100
	isort src tests --profile black

check: lint
	@echo "All quality checks passed"

# ===========================================
# Development
# ===========================================

run:
	python run_dev_server.py

localstack:
	docker compose -f docker-compose.localstack.yml up -d
	@echo "LocalStack started at http://localhost:4566"
	@echo "Run 'make localstack-setup' to initialize resources"

localstack-setup:
	python scripts/setup_localstack.py

localstack-stop:
	docker compose -f docker-compose.localstack.yml down

# ===========================================
# Cleanup
# ===========================================

clean:
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	rm -rf *.egg-info build dist
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.db" -delete
	rm -f briefing_*.md

# ===========================================
# Docker
# ===========================================

docker-build:
	docker build -t daily-briefing-agent .

docker-run:
	docker run -p 5000:5000 --env-file .env.local daily-briefing-agent
