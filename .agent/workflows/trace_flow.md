---
description: Trace data flow through API endpoints to database
---
Trace how data flows through the system from API to DB.

### 1. List all API routes
// turbo
```bash
cd backend && grep -rn "@router\." src/api src/features --include="*.py" | grep -E "(get|post|put|delete|patch)" | awk -F: '{print $1": "$3}'
```

### 2. Find all database models
```bash
cd backend && grep -rn "class.*Base" src/ --include="*.py" | grep -v "__pycache__" | grep "SQLAlchemy\|declarative"
```

### 3. Trace a specific endpoint
Replace `{function_name}` with the endpoint handler:
```bash
cd backend && grep -rn "{function_name}" src/ --include="*.py" | head -20
```

### 4. Find all Temporal workflows
```bash
cd backend && grep -rn "@workflow.defn" src/ --include="*.py"
```

### 5. Show dependency graph (requires pydeps)
```bash
cd backend && .venv/bin/pydeps src/api --cluster --max-bacon 2 -o deps.svg 2>/dev/null || echo "Install pydeps: pip install pydeps"
```
