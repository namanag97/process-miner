---
description: Run quick backend tests (fast feedback loop)
---
Run a quick subset of tests for fast feedback during development.

// turbo
```bash
cd backend && .venv/bin/python -m pytest tests/ -v --tb=short -x --timeout=30 -q
```

**Flags explained:**
- `-x` - Stop on first failure
- `--timeout=30` - Fail tests that take too long  
- `-q` - Quiet mode for cleaner output
