---
description: Find unused/dead code in the codebase
---
Identify unused exports, dependencies, and dead code.

### Frontend (using Knip)
// turbo
```bash
cd frontend-new && npx knip
```

Knip will report:
- Unused files
- Unused dependencies
- Unused exports
- Unlisted dependencies

### Backend (find unused imports)
```bash
cd backend && .venv/bin/python -m ruff check src/ --select F401
```

### Find potentially orphaned files
```bash
cd backend && find src -name "*.py" -type f | while read f; do
  base=$(basename "$f" .py)
  if [ "$base" != "__init__" ] && ! grep -rq "$base" src --include="*.py" | grep -v "$f" > /dev/null 2>&1; then
    echo "Potentially unused: $f"
  fi
done
```
