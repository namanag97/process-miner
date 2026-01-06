---
description: Auto-fix linting and formatting issues
---
Automatically fix common linting and formatting issues across both frontend and backend.

### Backend (Ruff auto-fix + format)
// turbo
```bash
cd backend && make lint-fix && make format
```

### Frontend (ESLint + Prettier)
```bash
cd frontend-new && npx eslint --fix . && npx prettier --write "src/**/*.{ts,tsx,css,json}"
```

### After fixing, verify no issues remain:

**Backend:**
```bash
cd backend && make check
```

**Frontend:**
```bash
cd frontend-new && npm run lint
```
