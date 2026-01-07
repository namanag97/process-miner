# E2E API Testing Suite

## Overview

Automated end-to-end testing framework that:
- 🔍 **Auto-discovers** all API endpoints from OpenAPI specification
- 🧪 **Batch tests** all endpoints using curl-based HTTP requests
- 🐛 **Auto-detects** bugs (500s, validation errors, auth issues, performance problems)
- 📝 **Generates** detailed, prioritized bug reports with reproduction steps

## Quick Start

### Prerequisites

- Backend server running at `http://localhost:8001`
- Python 3.7+
- `requests` library (usually already installed)

### Run Tests

```bash
# From backend root directory
./scripts/run_e2e_api_tests.sh
```

Or directly:

```bash
cd tests/e2e
python3 quick_test.py
```

### Check Results

Bug reports are saved to `tests/e2e/bug_reports/report_YYYYMMDD_HHMMSS.md`

## Architecture

### Core Components

1. **OpenAPI Parser** (`helpers/openapi_parser.py`)
   - Parses OpenAPI spec from `/openapi.json`
   - Extracts endpoints, parameters, schemas
   - Generates test data from JSON schemas

2. **Curl Generator** (`helpers/curl_generator.py`)
   - Creates curl commands for each endpoint
   - Handles auth headers, request bodies, path/query params
   - Formats commands for reproduction

3. **Bug Detector** (`bug_detector.py`)
   - Analyzes HTTP responses
   - Detects common issues with pattern matching
   - Categorizes and prioritizes bugs (P0-P3)

4. **Main Test Runner** (`e2e_api_tester.py`)
   - Orchestrates the complete test flow
   - Executes requests in domain order
   - Generates markdown reports

### Bug Detection Rules

| Pattern | Priority | Category |
|---------|----------|----------|
| HTTP 500 | P0 | Internal Server Error |
| Blocking I/O in async | P0 | Async/Sync Mixing |
| Database errors | P0 | Database |
| HTTP 422 | P1 | Validation |
| Auth errors on public endpoints | P1 | Authentication |
| HTTP 404 (unexpected) | P2 | Not Found |
| Response time > 5s | P2 | Performance |

## Configuration

Default configuration in `e2e_config.py`:

```python
base_url: "http://localhost:8001"
timeout_seconds: 30
slow_request_threshold_ms: 5000
bug_report_dir: "tests/e2e/bug_reports"
```

Custom configuration via YAML (optional):

```yaml
# tests/e2e/e2e_config.yaml
base_url: "http://localhost:8001"
timeout_seconds: 60
slow_request_threshold_ms: 3000
```

## Usage Examples

### Run Against Different Server

```bash
cd tests/e2e
python3 quick_test.py http://staging.example.com:8001
```

### Integration with CI/CD

```bash
# In your CI pipeline
./scripts/run_e2e_api_tests.sh

# Check exit code
if [ $? -ne 0 ]; then
  echo "E2E tests found P0 bugs - blocking deployment"
  exit 1
fi
```

### Manual Bug Reproduction

From any bug report, copy the curl command:

```bash
curl -X POST 'http://localhost:8001/api/v1/ocpm/discover' \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"dataset_id": "test-id", "algorithm": "im"}'
```

## Report Format

```markdown
# E2E API Test Report
Generated: 2026-01-07 13:45:00

## Summary
- Total Endpoints Tested: 150
- Passed: 120
- Failed: 30
- Bugs Found: 42

## P0 - Critical (8 issues)
### BUG-E2E-001: Internal Server Error on POST /api/v1/ocpm/discover
**Category**: Async/Sync Mixing
**Endpoint**: `POST /api/v1/ocpm/discover`
**Status Code**: 500
**Error**: blocking I/O operation in async context

**Root Cause**: Blocking I/O operation in async context
**Suggested Fix**: Use async-compatible file/network operations

**Reproduction**:
\```bash
curl -X POST 'http://localhost:8001/api/v1/ocpm/discover' ...
\```
```

## Limitations & Future Improvements

### Current Limitations

1. **Path Parameters**: Endpoints requiring path params are skipped
   - Example: `/api/v1/datasets/{dataset_id}`
   - Workaround: We'd need test data factories

2. **Complex Test Scenarios**: Only tests basic request/response
   - No multi-step workflows (yet)
   - No state validation across endpoints

3. **File Uploads**: Multipart form data not fully supported
   - File upload endpoints may be skipped

### Planned Improvements

1. **Test Data Integration**
   - Use `tests/factories.py` to generate valid IDs
   - Create sample datasets for process mining endpoints
   - Pre-seed database with test data

2. **Smart Path Params**
   - Auto-create resources before testing dependent endpoints
   - Example: Create dataset → Test dataset/{id} endpoints

3. **State Machine Integration**
   - Use existing `StateValidator` from `helpers/state_machine.py`
   - Validate state transitions during tests

4. **Parallel Execution**
   - Run independent endpoints in parallel
   - Respect rate limits

## Integration with Existing Tests

This suite **complements** the existing pytest E2E tests:

| Type | Use Case | Example |
|------|----------|---------|
| **Pytest E2E** | Complex user journeys | `test_journey_dataset_upload.py` |
| **Curl Suite** | Quick API validation | This framework |

Both are valuable:
- **Pytest**: Deep integration testing with state validation
- **Curl**: Fast, broad coverage for quick feedback

## Troubleshooting

### "Server not responding"

```bash
# Check if backend is running
curl http://localhost:8001/health

# Start backend
cd backend
make dev
```

### "Module not found" errors

```bash
# Install dependencies
pip install requests

# Optional: Install PyYAML for custom configs
pip install pyyaml
```

### No bugs found but you know there are issues

Check `exclude_patterns` in config - some endpoints may be filtered out.

## Contributing

To add new bug detection patterns:

1. Edit `bug_detector.py`
2. Add pattern in `analyze_response()` method
3. Define priority, category, root cause, suggested fix

Example:

```python
elif "timeout" in response_body.lower():
    bug = self._create_bug(
        priority=BugPriority.P1,
        title=f"Timeout on {method} {endpoint}",
        category="Timeout",
        root_cause="Request exceeded timeout threshold",
        suggested_fix="Optimize queries or increase timeout",
    )
```

## License

Internal tool for development and QA purposes.
