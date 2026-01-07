# System Overview: Process Mining SaaS

> **Full-Stack AI Agent Guide**: Understanding how the backend and frontend work together

**Last Updated**: 2026-01-07  
**Stack**: FastAPI + React + TypeScript + PM4Py + Temporal  
**Architecture**: Clean Architecture (Backend) + Feature-Sliced Design (Frontend)

---

## 🎯 What This System Does

A **Process Mining SaaS platform** that helps organizations analyze and optimize their business processes:

1. **Upload** event logs (CSV/XES files)
2. **Discover** process models (Alpha, Inductive, Heuristics miners)
3. **Analyze** performance (bottlenecks, cycle times, variants)
4. **Predict** outcomes (ML-powered predictions)
5. **Visualize** processes (DFG, Petri nets, BPMN)
6. **Monitor** conformance (deviations, alignments)

**Think of it as**: "Google Analytics for Business Processes" - upload logs, get insights instantly.

---

## 🏗️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       User Browser                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React SPA (Frontend)                                │  │
│  │  - TanStack Query (data fetching)                    │  │
│  │  - Ant Design (UI components)                        │  │
│  │  - Feature plugins (auto-registration)               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ▲ │
                     HTTP   │ │ WebSocket (optional)
                            │ ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  API Layer (19 routers)                              │  │
│  │  - Authentication, Datasets, Discovery, Analytics    │  │
│  │  - Auto-documented (OpenAPI/Swagger)                 │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Platform Layer (SaaS Infrastructure)                │  │
│  │  - Multi-tenancy (Org → Workspace → Project)         │  │
│  │  - Auth, Storage, Jobs, Temporal workflows           │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Feature Layer (Process Mining Domain)               │  │
│  │  - PM4Py integration (discovery, conformance)        │  │
│  │  - DuckDB/Arrow (10x faster CSV ingestion)           │  │
│  │  - ML models (scikit-learn, XGBoost)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Services                      │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌────────────┐  │
│  │ SQLite/  │  │  Redis   │  │ Temporal│  │ S3/MinIO   │  │
│  │PostgreSQL│  │ (Cache)  │  │(Workflows)  │ (Storage)  │  │
│  └──────────┘  └──────────┘  └─────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: User Journey Example

### Example: Upload and Analyze an Event Log

```
1. USER: Uploads CSV file via Upload Wizard
   ↓
2. FRONTEND: POST /api/v1/datasets/upload (multipart/form-data)
   ↓
3. BACKEND: Stores file in S3/MinIO
   ↓
4. BACKEND: Starts Temporal ingestion workflow (async)
   ↓
5. TEMPORAL WORKER: Parses CSV with DuckDB → PostgreSQL
   ↓
6. BACKEND: Updates dataset status → "ready"
   ↓
7. FRONTEND: Polls dataset status (TanStack Query auto-refetch)
   ↓
8. USER: Clicks "Discover Process" button
   ↓
9. FRONTEND: POST /api/v1/discovery/discover { miner: "inductive" }
   ↓
10. BACKEND: Loads events from DB → PM4Py log
    ↓
11. BACKEND: Runs Inductive Miner algorithm
    ↓
12. BACKEND: Serializes Petri net → saves to DB
    ↓
13. FRONTEND: Fetches discovered model
    ↓
14. FRONTEND: Renders process graph with Cytoscape.js
    ↓
15. USER: Views interactive process diagram
```

---

## 📁 Codebase Structure

### Backend Structure

```
backend/
├── src/
│   ├── platform/          # 🏢 SaaS Infrastructure
│   │   ├── core/           # Config, exceptions, security
│   │   ├── infrastructure/ # Cache, tasks, metrics
│   │   ├── workspaces/     # Multi-tenancy
│   │   ├── storage/        # File storage (S3)
│   │   └── temporal/       # Workflow orchestration
│   │
│   ├── features/          # 🎯 Process Mining Domain
│   │   └── process_mining/
│   │       ├── ingestion/  # CSV/XES parsing
│   │       ├── discovery/  # Mining algorithms
│   │       ├── analytics/  # Performance analysis
│   │       ├── predictions/# ML models
│   │       └── ocpm/       # Object-centric PM
│   │
│   ├── api/               # 🌐 API Layer
│   │   ├── main.py         # FastAPI app
│   │   └── routers/        # Endpoint definitions
│   │
│   └── shared/            # 🔄 Cross-cutting
│       └── database.py     # SQLAlchemy Base
│
├── alembic/               # Database migrations
├── tests/                 # Pytest tests
└── docs/                  # Comprehensive documentation
```

### Frontend Structure

```
frontend-new/
├── src/
│   ├── App.tsx            # 🏠 App shell
│   ├── features/          # 🎯 Feature Modules
│   │   ├── platform/       # Workspace, Projects, Settings
│   │   ├── explorer/       # Process visualization
│   │   ├── analytics/      # Performance dashboards
│   │   ├── ai/             # AI insights
│   │   └── discovery/      # Process discovery UI
│   │
│   ├── shared/            # 🔄 Shared Code
│   │   ├── design-system.ts # UI component library
│   │   ├── context/        # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   └── ui/             # Shared components
│   │
│   └── api/               # 🌐 API Integration
│       ├── client/         # Auto-generated SDK
│       └── hooks/          # TanStack Query hooks
│
├── public/                # Static assets
└── rspack.config.js       # Bundler config
```

---

## 🔗 Integration Points

### 1. API Communication

**OpenAPI Spec**: Backend auto-generates OpenAPI schema

```
Backend: http://localhost:8001/openapi.json
         ↓
Frontend: npm run generate:api (orval)
         ↓
Auto-generated: src/api/client/ (TypeScript types + functions)
```

**Usage in Frontend**:
```typescript
// Auto-generated types
import { Dataset, DiscoveryRequest } from '@/api/client/models';

// Auto-generated API functions
import { datasetsApi } from '@/api/client';

// TanStack Query wrapper
const { data } = useQuery({
  queryKey: ['datasets'],
  queryFn: () => datasetsApi.getAll(),
});
```

### 2. Real-Time Updates

**Pattern**: Polling with TanStack Query

```typescript
// Auto-refetch every 5 seconds
const { data } = useQuery({
  queryKey: ['dataset', id],
  queryFn: () => datasetsApi.getById(id),
  refetchInterval: 5000,
  enabled: data?.status === 'processing',
});
```

**Future**: WebSocket support for real-time notifications

### 3. File Uploads

**Backend Endpoint**: `POST /api/v1/datasets/upload`

```python
# backend/src/features/process_mining/ingestion/router.py
@router.post("/upload")
async def upload_dataset(file: UploadFile):
    # 1. Validate file
    # 2. Store in S3/MinIO
    # 3. Start Temporal ingestion workflow
    # 4. Return dataset ID
```

**Frontend Component**:
```typescript
// frontend/src/features/platform/workspace/UploadWizard.tsx
const mutation = useMutation({
  mutationFn: (file: File) => datasetsApi.upload(file),
  onSuccess: (dataset) => {
    navigate(`/workspace?dataset=${dataset.id}`);
  },
});
```

### 4. Error Handling

**Backend**: RFC 7807 Problem Details

```python
# Backend returns structured errors
{
  "type": "not_found",
  "title": "Dataset not found",
  "status": 404,
  "detail": "Dataset with ID 123 does not exist",
  "instance": "/api/v1/datasets/123"
}
```

**Frontend**: Error boundary + Query error handling

```typescript
// Global error boundary catches render errors
<GlobalErrorBoundary onError={handleError}>

// Query errors shown in UI
if (error) {
  return <ErrorAlert error={error} />;
}
```

---

## 🛠️ Development Workflow

### Full-Stack Setup

```bash
# Terminal 1: Backend
cd backend
source .venv/bin/activate
make dev                      # Start on :8001

# Terminal 2: Frontend
cd frontend-new
npm run start                 # Start on :4200

# Terminal 3: Temporal (if using workflows)
cd backend
make temporal-up              # Start Temporal server
make temporal-ingestion-worker

# Terminal 4: Temporal workers (optional)
make temporal-analysis-worker
```

### Available Workflows

Use predefined workflows (in `.agent/workflows/`):
- `/start_servers` - Start backend + frontend
- `/full_stack` - Start everything (BE + FE + Temporal)
- `/check_backend` - Run backend quality checks
- `/check_frontend` - Run frontend quality checks
- `/test_journeys` - Run E2E user journey tests

### Common Tasks

| Task | Backend | Frontend |
|------|---------|----------|
| **Run dev server** | `make dev` | `npm run start` |
| **Run tests** | `make test` | `npm test` |
| **Lint code** | `make lint` | `npm run lint` |
| **Type check** | `make typecheck` | Built into build |
| **Generate API client** | N/A | `npm run generate:api` |
| **Database migration** | `alembic upgrade head` | N/A |

---

## 🔍 Key Technologies

### Backend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web framework | 0.109+ |
| **Python** | Language | 3.10+ |
| **SQLAlchemy** | ORM | 2.0+ |
| **PM4Py** | Process mining | 2.7+ |
| **DuckDB** | Fast analytics | 1.0+ |
| **Temporal** | Workflow orchestration | 1.5+ |
| **Redis** | Cache + tasks | 5.0+ |
| **Pytest** | Testing | 7.4+ |

### Frontend Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 19.0 |
| **TypeScript** | Language | 5.9 |
| **TanStack Query** | Data fetching | 5.90+ |
| **Ant Design** | UI components | 5.29+ |
| **React Router** | Routing | 6.29+ |
| **Rspack** | Bundler | 1.5+ |
| **Nx** | Monorepo | 22.3+ |
| **Jest** | Testing | 30.0+ |

---

## 📚 Documentation Map

### For AI Agents

| Document | Purpose |
|----------|---------|
| **[Backend AI Agent Guide](file:///Users/namanagarwal/system/backend/AI_AGENT_GUIDE.md)** | Backend development guide |
| **[Frontend AI Agent Guide](file:///Users/namanagarwal/system/frontend-new/AI_AGENT_GUIDE.md)** | Frontend development guide |
| **[Backend Architecture](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md)** | Backend layer separation |
| **[Frontend Architecture](file:///Users/namanagarwal/system/frontend-new/ARCHITECTURE.md)** | Frontend architecture |
| **This Document** | Full-stack overview |

### For Developers

| Topic | Backend | Frontend |
|-------|---------|----------|
| **README** | [Backend README](file:///Users/namanagarwal/system/backend/README.md) | [Frontend README](file:///Users/namanagarwal/system/frontend-new/README.md) |
| **Setup Guide** | Backend AI Guide | Frontend AI Guide |
| **API Docs** | http://localhost:8001/docs | N/A |
| **Architecture** | [ARCHITECTURE.md](file:///Users/namanagarwal/system/backend/ARCHITECTURE.md) | [ARCHITECTURE.md](file:///Users/namanagarwal/system/frontend-new/ARCHITECTURE.md) |

---

## 🐛 Debugging Full-Stack Issues

### Issue: Frontend can't connect to backend

**Symptoms**: CORS errors, network failures

**Check**:
1. Backend running? `curl http://localhost:8001/health`
2. Correct API URL? Check `frontend-new/.env` → `VITE_API_BASE_URL`
3. CORS enabled? Check backend `src/api/main.py` CORS config

### Issue: API type mismatches

**Symptoms**: TypeScript errors, unexpected API responses

**Fix**:
1. Backend changed API? Regenerate client: `npm run generate:api`
2. Check OpenAPI spec: http://localhost:8001/openapi.json
3. Compare backend response vs. frontend types

### Issue: Data not updating

**Symptoms**: Stale data in UI

**Check**:
1. TanStack Query cache? Check React Query DevTools
2. Backend mutation successful? Check network tab
3. Cache invalidation? Check `invalidateQueries` calls

### Issue: Temporal workflow failures

**Symptoms**: Async jobs stuck, errors in logs

**Check**:
1. Temporal server running? http://localhost:8088
2. Workers running? Check terminal output
3. Workflow history? Check Temporal UI

---

## 🚀 Deployment (Future)

### Backend Deployment

```bash
# Docker build
docker build -t process-mining-backend .

# Environment variables
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
S3_BUCKET=...
JWT_SECRET=...

# Run
docker run -p 8001:8001 process-mining-backend
```

### Frontend Deployment

```bash
# Build
npm run build               # Output to dist/

# Deploy to static hosting
# - Vercel, Netlify, S3+CloudFront, etc.

# Environment variables
VITE_API_BASE_URL=https://api.example.com
```

---

## 📊 System Metrics

- **Backend**: ~50K lines of Python
- **Frontend**: ~40K lines of TypeScript
- **API Endpoints**: 80+ endpoints across 19 routers
- **Database Tables**: 23 tables (multi-tenant)
- **Features**: 6 major feature modules (frontend)
- **Test Coverage**: Backend 30%+, Frontend TBD

---

## 🎓 Learning Path for AI Agents

### Day 1: Orientation
1. Read this document
2. Explore backend structure: `ls backend/src/`
3. Explore frontend structure: `ls frontend-new/src/`
4. Run both servers locally

### Day 2-3: Backend Deep Dive
1. Read [Backend AI Agent Guide](file:///Users/namanagarwal/system/backend/AI_AGENT_GUIDE.md)
2. Study one feature (e.g., `src/features/process_mining/analytics/`)
3. Trace one API request end-to-end
4. Run backend tests

### Day 4-5: Frontend Deep Dive
1. Read [Frontend AI Agent Guide](file:///Users/namanagarwal/system/frontend-new/AI_AGENT_GUIDE.md)
2. Study one feature (e.g., `src/features/analytics/`)
3. Follow data flow from UI → API → Backend
4. Run frontend tests

### Week 2: Contribute
1. Fix a small bug or add a simple feature
2. Write tests for your changes
3. Run quality checks (lint, typecheck)
4. Document your changes

---

**Ready to start?** Choose a component (frontend or backend) and read its AI Agent Guide! 🚀
