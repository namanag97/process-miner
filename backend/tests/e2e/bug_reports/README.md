# Bug Reports Directory

This directory contains generated bug reports from E2E API testing.

Reports are automatically generated with filename format: `report_YYYYMMDD_HHMMSS.md`

## Report Structure

Each report contains:
- Test summary (endpoints tested, pass/fail counts, bugs found)
- Bugs grouped by priority (P0, P1, P2, P3)
- For each bug:
  - Title and category
  - Endpoint and HTTP method
  - Error details
  - Root cause analysis
  - Suggested fix
  - Curl command for reproduction
  - Response body

## Usage

Generated automatically when running:
```bash
./scripts/run_e2e_api_tests.sh
```

Or directly:
```bash
cd tests/e2e
python e2e_api_tester.py
```
