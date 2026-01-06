---
description: Run strict type checking across the stack
---
Catch type errors before they become runtime bugs.

### Backend (mypy strict)
// turbo
```bash
cd backend && .venv/bin/python -m mypy src/ --config-file pyproject.toml --show-error-codes
```

### Frontend (TypeScript strict)
```bash
cd frontend-new && npx tsc --noEmit --strict 2>&1 | head -50
```

### Find untyped functions (backend)
```bash
cd backend && grep -rn "def " src/ --include="*.py" | grep -v "-> " | grep -v "__pycache__" | head -20
```

### Find 'any' types (frontend)
```bash
cd frontend-new && grep -rn ": any" src/ --include="*.ts" --include="*.tsx" | head -20
```
