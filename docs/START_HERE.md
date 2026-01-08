# CLAUDE CODE: START HERE

## Your Mission

Get the Process Mining MVP pipeline working:

```
Login → Upload → Map → Ingest → Discover → Visualize → Analyze
```

## Quick Start

### 1. Start Backend

```bash
cd /Users/namanagarwal/system/backend/src
../.venv/bin/python -m uvicorn api.main:app --reload --port 8001
```

### 2. Start Frontend (Optional)

```bash
cd /Users/namanagarwal/system/frontend-new
npm run start
```

### 3. Test the API

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"TestPass123"}' | jq -r '.access_token')

echo "Token: $TOKEN"

# Get presigned URL for upload
curl -s -X POST http://localhost:8001/api/v1/datasets/presign \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"filename":"events.csv","project_id":"mvp-proj-001"}' | jq

# Health check
curl http://localhost:8001/health/live
```

## Dev Credentials

```
Email:    analyst@example.com
Password: TestPass123
```

Pre-seeded IDs:
- Organization: `mvp-org-001`
- Workspace: `mvp-ws-001`
- Project: `mvp-proj-001`
- User: `mvp-user-001`

## Key Directories

```
backend/src/
├── api/                 # FastAPI app and routers
├── features/            # Process mining features
│   └── process_mining/
│       ├── datasets/    # Dataset upload, ingestion
│       ├── discovery/   # Process discovery
│       ├── analytics/   # Performance analytics
│       └── visualization/ # DFG, Petri nets
├── infra/               # Infrastructure (auth, db, temporal)
└── shared/              # Shared utilities

frontend-new/src/
├── features/            # Feature modules
├── shared/              # Shared components
└── api/                 # API integration
```

## API Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Full Documentation

- `../CLAUDE.md` - Main project documentation
- `../backend/README.md` - Backend setup and API reference
- `../frontend-new/README.md` - Frontend setup and architecture
