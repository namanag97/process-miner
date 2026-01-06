---
description: Run full frontend quality checks (lint, typecheck, test)
---
Run all frontend quality checks to ensure code health.

### 1. Lint check
// turbo
```bash
cd frontend-new && npm run lint
```

### 2. TypeScript check
```bash
cd frontend-new && npx tsc --noEmit
```

### 3. Run tests
```bash
cd frontend-new && npm test
```

### Quick all-in-one (fails fast)
```bash
cd frontend-new && npm run lint && npx tsc --noEmit && npm test
```
