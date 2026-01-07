# Scripts CLAUDE.md

## Overview
Utility scripts for testing, auditing, and development workflows.

## Available Scripts

### ai_test_runner.sh
Automated AI-powered test runner for validating user journeys.

```bash
./scripts/ai_test_runner.sh
```

### test_user_journeys.sh
End-to-end user journey testing script. Tests complete workflows from upload to analysis.

```bash
./scripts/test_user_journeys.sh
```

### trace_journeys.sh
Traces and logs user journey paths through the application.

```bash
./scripts/trace_journeys.sh
```

### generate_audit_report.py
Python script to generate audit reports from test results.

```bash
python scripts/generate_audit_report.py
```

## Usage Notes

- Scripts assume backend is running on port 8001
- Most scripts require the backend virtual environment
- Test scripts may create test data in the database
