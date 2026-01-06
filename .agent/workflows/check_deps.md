---
description: Audit dependencies for security vulnerabilities and outdated packages
---
Check for vulnerable or outdated dependencies.

### Backend (Python)
// turbo
```bash
cd backend && .venv/bin/pip-audit 2>/dev/null || .venv/bin/pip install pip-audit && .venv/bin/pip-audit
```

### Check outdated backend packages
```bash
cd backend && .venv/bin/pip list --outdated
```

### Frontend (npm)
```bash
cd frontend-new && npm audit
```

### Check outdated frontend packages
```bash
cd frontend-new && npm outdated
```
