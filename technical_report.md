# Process Mining Platform - Technical Report

**Date:** December 16, 2025
**Scope:** Full Codebase Analysis (`process-miner`, `backend`, `src`)

---

## 1. Project Structure

The project follows a **monorepo-like structure** combining a Next.js frontend and a FastAPI backend.

### Top-Level Structure
- **`process-miner/`**: Root directory.
    - **`backend/`**: Python FastAPI application (REST API & Workers).
    - **`src/`**: Next.js React frontend source code.
    - **`scripts/`**: Utility scripts (setup, etc.).
    - **`Dockerfile.backend`, `Dockerfile.frontend`**: Containerization definitions.

### Entry Points & Initialization
- **Backend**: `backend/app/main.py`.
    - Initializes `FastAPI` app.
    - Configures `CORSMiddleware` and `Sentry`.
    - Bootstraps database tables via `lifespan` event.
    - Aggregates routers from `backend/app/routers/`.
- **Frontend**: `src/app/layout.tsx` (Next.js App Router).
    - Root layout likely containing providers (Theme, Query, etc.).
    - Pages located in `src/app/(dashboard)/...` and `src/app/(auth)/...`.

### Configuration
- **Backend**: `backend/app/config.py` (uses `pydantic-settings`).
- **Frontend**: `next.config.mjs`, `tailwind.config.ts`, `components.json`.
- **Environment**:
    - `.env` files used (e.g., `.env.example`).
    - Key variables detected: `DATABASE_URL`, `SENTRY_DSN`, `REDIS_URL` (implied for Celery), `FRONTEND_URL`.

---

## 2. Tech Stack Detection

### Frontend
- **Framework**: Next.js 16 (React 18).
- **Language**: TypeScript (`tsconfig.json`).
- **Styling**: Tailwind CSS, `tailwindcss-animate`, `class-variance-authority`.
- **Component Library**: Shadcn UI (Radix UI primitives).
- **State/Data Fetching**: `@tanstack/react-query`, `zustand`, `react-hook-form`, `zod`.
- **Visualization**: `recharts` (charts), `@xyflow/react` (React Flow) for process maps.
- **Utilities**: `date-fns`, `papaparse` (CSV parsing), `sonner` (toasts).

### Backend
- **Framework**: FastAPI (Python 3.11+).
- **Server**: Uvicorn.
- **ORM**: SQLModel (SQLAlchemy + Pydantic) with Async engine.
- **Database**: SQLite (currently `process_miner.db` for MVP/DEV), extensible to PostgreSQL.
- **Process Mining Engine**: `pm4py` (v2.7+).
- **Background Tasks**: Celery with Redis (implied by `dev:worker` script in `package.json` and imports).
- **Logging**: `structlog`.
- **Validation**: Pydantic v2.

---

## 3. Architecture Analysis

### Pattern
- **Client-Server (Monolithic Backend)**: The frontend is a SPA/SSR hybrid served by Next.js, communicating via REST API to a single FastAPI backend service.
- **Worker Pattern**: Long-running process mining tasks are offloaded to background workers (Celery) or run via async background tasks (MVP implementation in `processing.py` uses direct async execution but mimics a job system).

### Core Components & Data Flow
1.  **Upload Service**:
    - Receives CSV/XES files.
    - Parses locally (potential scalable bottleneck).
    - Stores metadata in `Upload` table.
2.  **Mapping Service**:
    - User maps columns (Case ID, Activity, Timestamp).
    - Validates mapping validity against file content.
3.  **Mining Service (`processing.py`)**:
    - **Trigger**: User requests processing for a specific mapping.
    - **Job Handling**: Creates a `Job` record (queued -> processing -> completed).
    - **Execution**:
        - Loads file from disk.
        - Converts to Event Log (PM4Py).
        - **Discovery**: Calculates DFG (Directly-Follows Graph).
        - **Analysis**: Computes Variants, Activity Stats, Deviations.
        - **Persistence**: Serializes all results into JSON blobs stored in `Dataset` table.
4.  **Analysis Service**:
    - Serves read-only analytics to frontend (Graph, Stats, Variants) from stored `Dataset`.

---

## 4. Process Mining Specifics

### Algorithms Implemented
- **Discovery**: Directly-Follows Graph (DFG) using `pm4py.discover_dfg`.
    - Includes performance DFG (durations) via `pm4py.discover_performance_dfg`.
- **Variants**: Standard variant extraction (`pm4py.get_variants`), sorted by frequency.
- **Conformance / Deviations**:
    - **Rework**: Custom rule-based detection (activity count > 1 in same case).
    - **Unusual Paths**: Custom rule-based detection (variant frequency < 1% and low count).
- **Statistics**:
    - Case durations (avg/median).
    - Throughput times.
    - Start/End activity distribution.

### Visualization
- **Graph**: React Flow (`@xyflow/react`) is used to render the DFG.
    - Backend transforms DFG nodes/edges into React Flow specific format (`backend/app/models/schemas.py`: `DFGNode`, `DFGEdge`).
- **Charts**: `recharts` used for variant distributions and frequency plots.

---

## 5. API & Database Schema

### Database Models (`backend/app/models/`)
- **`Upload`**: File metadata.
- **`Mapping`**: Column configuration (Case ID, Activity, Timestamp).
- **`Job`**: Async task tracking (Status, Progress, Error).
- **`Dataset`**: Stores heavy analysis results as JSON blobs (`dfg_json`, `variants_json`, etc.). *Note: This denotes a "document store" usage pattern within SQL.*
- **`Process`, `Organization`, `User`**: Standard entity management (likely unused or basic in MVP).

### Key API Endpoints
- `POST /api/uploads`: File upload.
- `POST /api/mappings`: Create column mapping.
- `POST /api/processing/{mapping_id}`: Start mining job.
- `GET /api/processing/jobs/{job_id}`: Poll job status.
- `GET /api/analysis/{dataset_id}/...`: Retrieve specific analysis (DFG, variants).

---

## 6. Code Quality Assessment

### Strengths
- **Type Safety**: Heavy usage of Pydantic and TypeScript ensures contract safety.
- **Modern Stack**: Uses latest versions (Next.js 16, Pydantic v2, SQLModel).
- **Structure**: Clear separation of `routers`, `services`, and `models`.

### Areas for Improvement
- **Blocking Operations**: File I/O and PM4Py CPU-intensive tasks are run in the main async loop or default thread pool. This will block the event loop under load.
    - *Fix*: Use `run_in_executor` with `ProcessPoolExecutor` for mining tasks.
- **Large JSON Blobs**: Storing entire analysis results (DFG, Variants) in single database columns (`Dataset` table) is simple but inefficient for large logs.
- **Error Handling**: `try/except` blocks in `run_mining_job` are broad. Granular handling for parsing vs. mining errors is better.

---

## 7. Security Scan

### Current Status
- **Authentication**: Basic `users_router` exists, but `main.py` shows no global `AuthenticationMiddleware`. Auth seems fully open or rudimentary for the MVP.
- **Input Validation**: Strong. Pydantic schemas validate all incoming JSON and file structures.
- **File Security**: File uploads seem to be stored locally. Path traversal protection relies on generic UUID generation but needs explicit verification.
- **Secrets**: `.env` usage is correct. No hardcoded secrets found in reviewed code.

### Vulnerabilities
- **DoS Risk**: Large file uploads or complex mining jobs can easily exhaust server RAM/CPU since there are no apparent resource quotas or stream processing.

---

## 8. Technical Debt & Improvements

1.  **Refactor Mining Execution**: Move `pm4py` calls to a dedicated worker process (Celery is referenced in scripts but `processing_service.py` seems to run inline/async).
2.  **Streaming Uploads**: Use streaming for file parsing to avoid loading entire files into memory dataframe `pd.read_csv`.
3.  **Database Normalization**: Break down `Dataset` JSON blobs into relational tables for queried access (e.g., `Variant` table, `Activity` table) if analytics needs filtering.
4.  **Logging**: Enhance `structlog` usage to trace `request_id` across frontend -> backend -> worker.
