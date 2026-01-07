# Backend Tests CLAUDE.md

## Overview
Test suite for the backend application. Organized by test type with shared fixtures and factories.

## Directory Structure

```
tests/
├── conftest.py              # Pytest fixtures (test client, DB session, auth)
├── factories.py             # Test data factories
├── mocks.py                 # Mock objects for external services
├── api/                     # API endpoint tests (integration)
├── e2e/                     # End-to-end workflow tests
├── integration/             # Service integration tests
├── unit/                    # Unit tests for isolated components
├── data/                    # Test data files
└── test_*.sh                # Shell-based API test scripts
```

## Running Tests

```bash
# All tests
cd backend && .venv/bin/python -m pytest tests/ -v

# By type
.venv/bin/python -m pytest tests/api/ -v      # API tests
.venv/bin/python -m pytest tests/unit/ -v     # Unit tests
.venv/bin/python -m pytest tests/e2e/ -v      # E2E tests

# Single file
.venv/bin/python -m pytest tests/api/test_datasets.py -v

# With coverage
.venv/bin/python -m pytest tests/ --cov=src --cov-report=html
```

## Key Files

### conftest.py
Global fixtures including:
- `test_client` - FastAPI TestClient
- `db_session` - Async database session
- `authenticated_user` - Pre-authenticated test user
- `test_dataset` - Sample dataset for tests

### factories.py
Factory classes for generating test data:
- `UserFactory`, `DatasetFactory`, `ProjectFactory`, etc.

### mocks.py
Mock implementations:
- `MockStorageClient` - S3/MinIO mock
- `MockCeleryTask` - Task queue mock

## Test Patterns

### API Test
```python
async def test_get_dataset(test_client, test_dataset):
    response = await test_client.get(f"/api/v1/datasets/{test_dataset.id}")
    assert response.status_code == 200
```

### Service Test
```python
async def test_dataset_service(db_session):
    service = DatasetService(db_session)
    result = await service.create(...)
    assert result.id is not None
```

## Shell Test Scripts

- `test_api_curl.sh` - Quick curl-based API smoke tests
- `test_api_e2e.sh` - Full E2E workflow via curl
- `test_full_workflow.sh` - Complete user journey test
