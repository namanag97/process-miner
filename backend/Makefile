# Process Mining SaaS - Backend Makefile
# Python-specific development commands

.PHONY: help install lint format typecheck security test run clean

# Use the virtual environment Python
PYTHON = .venv/bin/python
PIP = .venv/bin/pip

help:
	@echo "Backend Development Commands"
	@echo ""
	@echo "  make install   - Install dependencies"
	@echo "  make lint      - Run Ruff linter"
	@echo "  make format    - Format code with Ruff"
	@echo "  make typecheck - Run mypy type checker"
	@echo "  make security  - Run Bandit security scanner"
	@echo "  make test      - Run pytest tests"
	@echo "  make test-cov  - Run tests with coverage"
	@echo "  make run       - Start dev server"
	@echo "  make check     - Run all checks"

install:
	$(PIP) install -e ".[dev,observability]"

lint:
	$(PYTHON) -m ruff check src/ tests/

lint-fix:
	$(PYTHON) -m ruff check src/ tests/ --fix

format:
	$(PYTHON) -m ruff format src/ tests/

format-check:
	$(PYTHON) -m ruff format --check src/ tests/

typecheck:
	$(PYTHON) -m mypy src/ --config-file pyproject.toml

security:
	$(PYTHON) -m bandit -r src/ -c pyproject.toml

test:
	$(PYTHON) -m pytest tests/ -v --tb=short

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term

check: lint format-check typecheck security
	@echo "✅ All checks passed"

run:
	$(PYTHON) -m uvicorn src.main:app --reload --port 8001

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
