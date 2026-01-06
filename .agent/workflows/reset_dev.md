---
description: Reset development environment (clean cache, logs, reset DB)
---
Use this to reset your local development environment when things get messy.

### Light cleanup (logs + cache only)
// turbo
```bash
cd backend && make clean-dev
```

### Full reset (including database)
⚠️ **Warning**: This will delete your local database!

```bash
cd backend && make reset-dev
```

### What gets cleaned:
- Log files (celery.log, server.log, etc.)
- Temp storage (uploads, exports)
- Python cache (__pycache__, .pyc files)
- Database reset runs fresh migrations
