# Process Mining SaaS - Root Makefile
# Unified commands for linting, testing, and code quality

.PHONY: help install lint typecheck security test check all clean

# Use the backend's virtual environment Python (absolute reference from root)
BACKEND_VENV = backend/.venv/bin
BACKEND_PYTHON = $(BACKEND_VENV)/python
BACKEND_PIP = $(BACKEND_VENV)/pip

# Default target
help:
	@echo "Process Mining SaaS - Development Commands"
	@echo ""
	@echo "Quick Commands:"
	@echo "  make install    - Install all dependencies"
	@echo "  make lint       - Run all linters (Ruff + ESLint)"
	@echo "  make typecheck  - Run type checkers (mypy + tsc)"
	@echo "  make security   - Run security scans (Bandit)"
	@echo "  make test       - Run all tests (pytest + vitest)"
	@echo "  make check      - Run lint + typecheck + security"
	@echo "  make all        - Run check + test (full CI)"
	@echo ""
	@echo "Component Commands:"
	@echo "  make backend-*  - Run commands for backend only"
	@echo "  make sdk-*      - Run commands for SDK only"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make pre-commit - Install pre-commit hooks"
	@echo "  make dev        - Start development server"

# =============================================================================
# Installation
# =============================================================================

install: backend-install sdk-install
	@echo "✅ All dependencies installed"

backend-install:
	$(BACKEND_PIP) install -e "backend/.[dev,observability]"

sdk-install:
	cd sdk && npm install

pre-commit:
	$(BACKEND_PIP) install pre-commit
	cd backend && ../.venv/bin/python -m pre_commit install || true
	@echo "✅ Pre-commit hooks installed"

# =============================================================================
# Linting
# =============================================================================

lint: backend-lint sdk-lint
	@echo "✅ All linting passed"

backend-lint:
	@echo "🔍 Linting backend (Ruff)..."
	$(BACKEND_PYTHON) -m ruff check backend/src/ backend/tests/
	$(BACKEND_PYTHON) -m ruff format --check backend/src/ backend/tests/

sdk-lint:
	@echo "🔍 Linting SDK (ESLint + Prettier)..."
	cd sdk && npm run lint
	cd sdk && npm run format:check

# =============================================================================
# Type Checking
# =============================================================================

typecheck: backend-typecheck sdk-typecheck
	@echo "✅ All type checking passed"

backend-typecheck:
	@echo "🔍 Type checking backend (mypy)..."
	$(BACKEND_PYTHON) -m mypy backend/src/ --config-file backend/pyproject.toml

sdk-typecheck:
	@echo "🔍 Type checking SDK (tsc)..."
	cd sdk && npm run typecheck

# =============================================================================
# Security Scanning
# =============================================================================

security: backend-security
	@echo "✅ Security scan complete"

backend-security:
	@echo "🔒 Security scanning backend (Bandit)..."
	$(BACKEND_PYTHON) -m bandit -r backend/src/ -c backend/pyproject.toml

# =============================================================================
# Testing
# =============================================================================

test: backend-test sdk-test
	@echo "✅ All tests passed"

backend-test:
	@echo "🧪 Testing backend (pytest)..."
	cd backend && .venv/bin/python -m pytest tests/ -v --tb=short

backend-test-cov:
	@echo "🧪 Testing backend with coverage..."
	cd backend && .venv/bin/python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

sdk-test:
	@echo "🧪 Testing SDK (vitest)..."
	cd sdk && npm run test

# =============================================================================
# Combined Commands
# =============================================================================

check: lint typecheck security
	@echo ""
	@echo "══════════════════════════════════════════════════════════════"
	@echo "✅ All checks passed (lint + typecheck + security)"
	@echo "══════════════════════════════════════════════════════════════"

all: check test
	@echo ""
	@echo "══════════════════════════════════════════════════════════════"
	@echo "✅ Full CI passed (check + test)"
	@echo "══════════════════════════════════════════════════════════════"

# =============================================================================
# Development
# =============================================================================

dev:
	cd backend && .venv/bin/python -m uvicorn src.main:app --reload --port 8001

dev-observability:
	$(BACKEND_PIP) install -e "backend/.[observability]" && cd backend && .venv/bin/python -m uvicorn src.main:app --reload --port 8001

# =============================================================================
# Frontend Commands
# =============================================================================

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npx nx dev process-mining

frontend-build:
	cd frontend && npx nx build process-mining

frontend-lint:
	@echo "🔍 Linting frontend (ESLint)..."
	cd frontend && npx nx lint process-mining

frontend-typecheck:
	@echo "🔍 Type checking frontend (tsc)..."
	cd frontend && npx nx typecheck process-mining

frontend-test:
	@echo "🧪 Testing frontend (vitest)..."
	cd frontend && npx nx test ui
	cd frontend && npx nx test process-graph
	cd frontend && npx nx test api

frontend-e2e:
	@echo "🧪 E2E testing frontend (Playwright)..."
	cd frontend && npx nx e2e process-mining-e2e

# =============================================================================
# Cleanup
# =============================================================================

clean:
	rm -rf backend/.pytest_cache backend/.mypy_cache backend/.ruff_cache
	rm -rf sdk/dist sdk/node_modules/.cache
	rm -rf frontend/dist frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned up cache files"

