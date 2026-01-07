# Test CLAUDE.md

## Overview
Integration and end-to-end test suite for the platform. Contains test modules, E2E tests, and test reports.

## Directory Structure

```
test/
├── conftest.py              # Pytest fixtures and configuration
├── test_config.py           # Test environment configuration
├── test_plan.md             # Test plan documentation
├── modules/                 # Module-specific tests
├── e2e/                     # End-to-end test scenarios
├── e2e_test_event_log.csv   # Sample event log for E2E tests
├── test_results.json        # Latest test results
├── test_summary.md          # Test summary report
└── bugs_identified.md       # Known bugs from testing
```

## Running Tests

```bash
# Run all tests from project root
cd test && python -m pytest -v

# Run specific module tests
python -m pytest modules/test_datasets.py -v

# Run E2E tests
python -m pytest e2e/ -v
```

## Test Reports

- `test_results.json` - Machine-readable test results
- `test_summary.md` - Human-readable summary
- `bugs_identified.md` - Tracked bugs found during testing
- `test_report_*.txt` - Historical test run reports

## Adding Tests

1. Create test file in appropriate directory (`modules/` or `e2e/`)
2. Use fixtures from `conftest.py`
3. Follow existing test patterns
4. Update `test_plan.md` for new test coverage
