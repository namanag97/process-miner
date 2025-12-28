# Process Mining SDK - Makefile
# TypeScript-specific development commands

.PHONY: help install lint format typecheck test build clean

help:
	@echo "SDK Development Commands"
	@echo ""
	@echo "  make install   - Install dependencies"
	@echo "  make lint      - Run ESLint"
	@echo "  make format    - Format code with Prettier"
	@echo "  make typecheck - Run TypeScript type checker"
	@echo "  make test      - Run Vitest tests"
	@echo "  make build     - Build the SDK"
	@echo "  make check     - Run all checks"

install:
	npm install

lint:
	npm run lint

lint-fix:
	npm run lint:fix

format:
	npm run format

format-check:
	npm run format:check

typecheck:
	npm run typecheck

test:
	npm run test

build:
	npm run build

check: lint typecheck format-check
	@echo "✅ All checks passed"

clean:
	rm -rf dist node_modules/.cache
