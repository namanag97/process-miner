---
description: Run tests with coverage reports
---
Generate test coverage reports to identify untested code.

### Backend coverage
// turbo
```bash
cd backend && make test-cov
```

Coverage report will be:
- Printed to terminal
- HTML report at `backend/htmlcov/index.html`

### Open HTML coverage report
```bash
open backend/htmlcov/index.html
```

### Frontend coverage
```bash
cd frontend-new && npm test -- --coverage
```
