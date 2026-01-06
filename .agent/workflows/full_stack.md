---
description: Start the complete full-stack environment (Backend + Frontend + Temporal)
---
// turbo-all

Start all services needed for full local development.

### Step 1: Start Temporal infrastructure
```bash
cd backend && make temporal-up
```

### Step 2: Start Temporal workers (in background)
```bash
cd backend && make temporal-workers
```

### Step 3: Start Backend API
```bash
cd backend && make dev
```

### Step 4: Start Frontend (in a new terminal)
```bash
cd frontend-new && npm start
```

---

**Services will be available at:**
| Service | URL |
|---------|-----|
| Frontend | http://localhost:4200 |
| Backend API | http://localhost:8001/api/v1 |
| API Docs | http://localhost:8001/docs |
| Temporal UI | http://localhost:8088 |

---

### To stop everything:
```bash
cd backend && make temporal-stop && make temporal-down && make stop
```
