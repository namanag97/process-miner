# E2E User Journey Test Runner

A fast, curl-based test framework for simulating user journeys from the frontend perspective.

## Quick Start

```bash
# Run all journeys
cd test/e2e
pytest -v journeys/

# Run specific journey
pytest -v journeys/test_journey_02_upload.py

# With debug output
pytest -v -s journeys/

# Quick smoke test
pytest -v -m smoke journeys/
```

## User Journeys

| # | Journey | File | Description |
|---|---------|------|-------------|
| 1 | Onboarding | `test_journey_01_onboarding.py` | Register → Login → Create Project |
| 2 | **Upload** | `test_journey_02_upload.py` | Upload → Map → Ingest → Ready |
| 3 | Discovery | `test_journey_03_discovery.py` | Select Dataset → DFG → Model |
| 4 | Analytics | `test_journey_04_analytics.py` | Bottlenecks → Rework → Metrics |

## Debugging

Failed tests dump state to `debug_dumps/`. Each dump includes:
- Test context (IDs, tokens)
- Request/response details
- Error message

## Configuration

Environment variables:
- `API_BASE_URL` - Backend URL (default: `http://localhost:8001`)
