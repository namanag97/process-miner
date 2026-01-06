# Process Mining SaaS - Backend Makefile
# Python-specific development commands

.PHONY: help install lint format typecheck security test run dev restart stop clean

# Use the virtual environment Python
PYTHON = .venv/bin/python
PIP = .venv/bin/pip
PORT = 8001

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
	@echo "  make check     - Run all checks"
	@echo ""
	@echo "  make dev       - Start dev server (auto-restart, kills port first)"
	@echo "  make run       - Start dev server (simple)"
	@echo "  make restart   - Restart dev server"
	@echo "  make stop      - Stop dev server"

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
	$(PYTHON) -m uvicorn src.api.main:app --reload --port $(PORT)

dev:
	@echo "🔄 Starting dev server on port $(PORT)..."
	@# Kill any process on the port
	@lsof -ti:$(PORT) 2>/dev/null | xargs kill -9 2>/dev/null || true
	@# Wait for port to be free
	@sleep 1
	@# Start server
	@echo "🚀 Launching uvicorn..."
	@$(PYTHON) -m uvicorn src.api.main:app --reload --port $(PORT)

restart: dev

stop:
	@echo "⏸️  Stopping server on port $(PORT)..."
	@lsof -ti:$(PORT) 2>/dev/null | xargs kill -9 2>/dev/null || echo "No server running on port $(PORT)"

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# ============================================================================
# Cleanup Targets (Operational Stability)
# ============================================================================

.PHONY: clean-logs clean-storage clean-cache clean-dev reset-dev

clean-logs:
	@echo "🧹 Cleaning log files..."
	rm -f celery.log celery_debug*.log server*.log
	rm -f data/logs/*.log 2>/dev/null || true
	rm -f *.log
	@echo "✅ Logs cleaned"

clean-storage:
	@echo "🧹 Cleaning temp storage..."
	rm -rf data/storage/pm-raw-dev/* 2>/dev/null || true
	rm -rf data/exports/* 2>/dev/null || true
	rm -rf data/uploads/* 2>/dev/null || true
	@echo "✅ Storage cleaned"

clean-cache: clean
	@echo "🧹 Cleaning Python cache..."
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-dev: clean-logs clean-storage clean-cache
	@echo "🧹 Full dev cleanup complete"

reset-dev: clean-dev
	@echo "🔄 Resetting database..."
	rm -f process_mining.db data/app.db 2>/dev/null || true
	$(PYTHON) -m alembic upgrade head
	@echo "✅ Dev environment reset"

# ============================================================================
# Temporal Workflow Orchestration
# ============================================================================

.PHONY: temporal-up temporal-down temporal-logs temporal-ui temporal-workers temporal-stop

temporal-up:
	@echo "🚀 Starting Temporal server..."
	@docker-compose -f docker-compose.temporal.yml up -d
	@echo "✅ Temporal server running"
	@echo "   - gRPC API: localhost:7233"
	@echo "   - Web UI: http://localhost:8088"

temporal-down:
	@echo "⏹️  Stopping Temporal server..."
	@docker-compose -f docker-compose.temporal.yml down
	@echo "✅ Temporal server stopped"

temporal-logs:
	@docker-compose -f docker-compose.temporal.yml logs -f temporal

temporal-ui:
	@echo "🌐 Opening Temporal Web UI..."
	@open http://localhost:8088 2>/dev/null || xdg-open http://localhost:8088 2>/dev/null || echo "Open http://localhost:8088 in your browser"

temporal-workers:
	@echo "🏃 Starting Temporal workers..."
	@echo "Not yet implemented - will start all workers"
	# TODO: Implement in Phase 3
	# $(PYTHON) -m src.platform.temporal.workers.ingestion_worker &
	# $(PYTHON) -m src.platform.temporal.workers.analysis_worker &
	# $(PYTHON) -m src.platform.temporal.workers.ml_worker &

temporal-stop:
	@echo "⏹️  Stopping Temporal workers..."
	@pkill -f "temporal.workers" 2>/dev/null || echo "No workers running"

temporal-status:
	@echo "📊 Temporal status:"
	@docker-compose -f docker-compose.temporal.yml ps
