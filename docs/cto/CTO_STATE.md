# CTO STATE — ATLAS Process Mining Platform

Last Updated: 2026-01-02T20:02:00+05:30  
Current Sprint: #0 (Pre-MVP Sprint Planning)

---

## 🏗️ ARCHITECTURE OVERVIEW

### System Components

| Component                 | Technology                       | Purpose                                     | Status        | Notes                                  |
| ------------------------- | -------------------------------- | ------------------------------------------- | ------------- | -------------------------------------- |
| **Backend API**           | FastAPI + Python 3.11            | REST API, business logic, PM4Py integration | ✅ Running    | Port 8001, `make run` in /backend      |
| **Frontend**              | React 18 + TypeScript + Nx       | SPA with feature-based architecture         | ✅ Running    | Port 4200, `nx serve` in /frontend-new |
| **Database**              | SQLite (dev) → PostgreSQL (prod) | Data persistence, ORM via SQLAlchemy        | ✅ Working    | ~25 ORM models defined                 |
| **Process Mining Engine** | PM4Py                            | Discovery, conformance, analytics           | ✅ Integrated | 15+ miner algorithms available         |
| **Cache (Optional)**      | Redis                            | Session cache, job queues                   | ⚪ Configured | Not required for MVP                   |
| **Task Queue (Optional)** | Celery                           | Async job processing                        | ⚪ Configured | Mock implementation in place           |

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ATLAS DATA FLOW                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Frontend │────▶│ FastAPI      │────▶│ PM4Py        │────▶│ Response     │  │
│  │ (React)  │◀────│ Backend      │◀────│ Mining       │◀────│ Transform    │  │
│  └──────────┘    └──────────────┘    └──────────────┘    └──────────────┘  │
│       │                 │                                                    │
│       │                 ▼                                                    │
│       │          ┌──────────────┐                                           │
│       │          │ SQLite/PG    │                                           │
│       │          │ (Dataset,    │                                           │
│       │          │ Models, etc) │                                           │
│       │          └──────────────┘                                           │
│       │                 │                                                    │
│       │                 ▼                                                    │
│       │          ┌──────────────┐                                           │
│       │          │ File Storage │ ← CSV/XES uploads                         │
│       │          │ (./data/)    │                                           │
│       │          └──────────────┘                                           │
│       │                                                                      │
│       ▼                                                                      │
│  User uploads CSV → Backend validates → Stores in DB → PM4Py discovers →   │
│  Frontend visualizes DFG/Petri Net                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Technical Decisions

| Decision                                | Rationale                                          | Date         |
| --------------------------------------- | -------------------------------------------------- | ------------ |
| **DuckDB for fast ingestion**           | 10x faster than ORM iteration for large CSV files  | Recent       |
| **Feature-based frontend structure**    | Scalable, lazy-loaded modules per feature          | Architecture |
| **Mock auth for MVP**                   | Faster development, real auth deferred             | Strategic    |
| **SQLite for dev, PostgreSQL for prod** | Easy local setup, production-ready schema          | Architecture |
| **PM4Py as mining engine**              | Industry standard, comprehensive algorithm support | Foundational |

---

## 🔧 TECHNICAL STATUS

### Health by Component

| Component             | Health   | Reason                                             |
| --------------------- | -------- | -------------------------------------------------- |
| **Backend API Layer** | 🟢 Good  | 38 endpoints, clean FastAPI setup, RFC 7807 errors |
| **ORM/Database**      | 🟢 Good  | 25 models, proper relationships, migrations ready  |
| **PM4Py Integration** | 🟢 Good  | 15+ algorithms, DFG with performance, conformance  |
| **Frontend Shell**    | 🟢 Good  | Ant Design, routing, lazy loading                  |
| **Upload Flow**       | 🟡 Fair  | Works E2E but some edge cases may need polish      |
| **Process Explorer**  | 🟡 Fair  | DFG visualization works; missing some polish       |
| **Authentication**    | 🔴 Mock  | MOCK_USERS dict, any password accepted             |
| **Integrations**      | 🔴 Mock  | SAP, Salesforce, JIRA connectors are fake          |
| **Predictions**       | 🔴 Mock  | Statistical approximations, not real ML            |
| **Variant Analysis**  | 🔴 Basic | 33% coverage, missing drill-down, filtering        |

### API Endpoints Summary (38 Total)

```
/api/v1/datasets     → 15+ routes (CRUD, upload, preview, stats, variants)
/api/v1/discovery    →  8 routes (miners, discover, DFG, Petri net, quality)
/api/v1/conformance  →  8 routes (check, alignments, patterns, quality)
/api/v1/performance  →  6 routes (analyze, summary, bottlenecks, histogram)
/api/v1/org          →  5 routes (resources, handover, working-together, roles)
/api/v1/workspaces   →  5+ routes (CRUD, workspace management)
/api/v1/projects     →  5+ routes (CRUD, project management)
```

### Current Feature Coverage (from phased_development.md)

| Feature              | Coverage | Gap Analysis                                    |
| -------------------- | -------- | ----------------------------------------------- |
| Event Log Ingestion  | 90%      | Missing: advanced validation, error recovery    |
| Process Discovery    | 53%      | Missing: export, param config, model comparison |
| Conformance Checking | 45%      | Missing: reports, scheduling, trends            |
| Performance Analysis | 40%      | Missing: KPI dashboards, SLA monitoring         |
| Org Mining           | 47%      | Missing: resource timeline, team comparison     |
| Variant Analysis     | 33%      | Missing: filtering, drill-down, comparison      |

### Known Bugs / Issues

| Issue                             | Severity               | Hypothesis                       | Location                      |
| --------------------------------- | ---------------------- | -------------------------------- | ----------------------------- |
| **Auth accepts any password**     | 🔴 Critical (for prod) | Intentional mock for MVP         | `backend/.../auth_service.py` |
| **No persistent sessions**        | 🟡 Medium              | In-memory storage only           | `auth_service.py`             |
| **Discovery export missing**      | 🟡 Medium              | Endpoint exists, UI not wired    | `discovery.py` router         |
| **Variant drill-down incomplete** | 🟡 Medium              | Backend exists, frontend partial | Explorer feature              |

### Technical Debt

| Item                                | Impact              | Effort | Priority         |
| ----------------------------------- | ------------------- | ------ | ---------------- |
| **Mock auth → Real auth**           | High (security)     | Medium | Post-MVP         |
| **Mock integrations → Real APIs**   | Medium (enterprise) | High   | Enterprise phase |
| **In-memory queues → Redis/Celery** | Medium (scale)      | Medium | Scale phase      |
| **Model export to BPMN/PNML**       | Low (nice-to-have)  | Low    | Sprint 2+        |
| **Frontend test coverage**          | Medium (quality)    | High   | Ongoing          |

---

## 🚫 TECHNICAL RULES (For Dev Agents)

### 1. Authentication Rules

- **DO NOT** implement real authentication in MVP — use the existing mock
- **DO NOT** store real passwords or PII in the mock system
- When auth is needed, stub with guest/mock user

### 2. Database Rules

- **DO** follow existing ORM patterns in `backend/src/models/orm.py`
- **DO** use Alembic for any schema changes (when implemented)
- **DO NOT** modify SQLite file directly; use SQLAlchemy

### 3. File Location Rules

- **Backend services** → `/backend/src/services/`
- **Backend routers** → `/backend/src/api/routers/`
- **Frontend features** → `/frontend-new/src/features/{feature}/`
- **Frontend pages** → `/frontend-new/src/pages/` (for shared pages)
- **Docs** → `/docs/` (organized by role: ceo/, cto/, cpo/)

### 4. Error Handling Rules

- **DO** use RFC 7807 Problem Details format (already configured)
- **DO** use `AppException` from `backend/src/core/exceptions.py`
- **DO NOT** return raw 500 errors; always wrap with structured response

### 5. PM4Py Integration Rules

- **DO** use `MiningService` from `/backend/src/services/mining.py`
- **DO** use fast DuckDB path via `event_log_loader` for large logs
- **DO NOT** iterate over ORM objects for PM4Py conversion (too slow)

---

## 📁 FILE INDEX

### Backend Key Files

| Concern               | Location                                    | Notes                           |
| --------------------- | ------------------------------------------- | ------------------------------- |
| **API Entry Point**   | `/backend/src/api/main.py`                  | FastAPI app factory             |
| **All Routers**       | `/backend/src/api/routers/`                 | 20+ router files                |
| **ORM Models**        | `/backend/src/models/orm.py`                | 25 SQLAlchemy models            |
| **Pydantic Schemas**  | `/backend/src/models/schemas.py`            | Request/response DTOs           |
| **Database Setup**    | `/backend/src/models/database.py`           | Connection, init                |
| **PM4Py Service**     | `/backend/src/services/mining.py`           | 1300+ lines, all mining ops     |
| **Ingestion Service** | `/backend/src/services/ingestion.py`        | CSV/XES parsing                 |
| **DuckDB Fast Path**  | `/backend/src/services/event_log_loader.py` | 10x faster loading              |
| **Configuration**     | `/backend/src/core/config.py`               | Pydantic settings               |
| **Exceptions**        | `/backend/src/core/exceptions.py`           | RFC 7807 errors                 |
| **Infrastructure**    | `/backend/src/infrastructure/`              | Cache, circuit breaker, metrics |

### Frontend Key Files

| Concern               | Location                                            | Notes                    |
| --------------------- | --------------------------------------------------- | ------------------------ |
| **App Entry**         | `/frontend-new/src/App.tsx`                         | Routes, providers        |
| **Explorer Feature**  | `/frontend-new/src/features/explorer/`              | DFG visualization        |
| **Projects Feature**  | `/frontend-new/src/features/projects/`              | Project management       |
| **Analytics Feature** | `/frontend-new/src/features/analytics/`             | Performance, conformance |
| **Upload Wizard**     | `/frontend-new/src/pages/logs/UploadWizardPage.tsx` | CSV/XES upload           |
| **Styles**            | `/frontend-new/src/styles.css`                      | Global CSS               |
| **Core Components**   | `/frontend-new/src/core/`                           | Shared hooks, plugins    |

### Documentation Files

| Document               | Location                      | Purpose                 |
| ---------------------- | ----------------------------- | ----------------------- |
| **Phased Development** | `/docs/phased_development.md` | Current status, roadmap |
| **Database Docs**      | `/docs/DATABASE_docs.md`      | Schema overview         |
| **DBML Schema**        | `/docs/database_schema.dbml`  | Visualizable schema     |
| **Mock Data Notice**   | `/docs/MOCK_DATA_NOTICE.md`   | What's fake             |
| **User Flow**          | `/userflow.md`                | All UI interactions     |
| **Business Use Cases** | `/docs/businessusecase.md`    | 237 activities          |
| **CEO State**          | `/docs/ceo/CEO_STATE.md`      | Executive dashboard     |
| **CTO State**          | `/docs/cto/CTO_STATE.md`      | This document           |

---

## 📋 DEV TASK QUEUE

_Empty — will be populated after Sprint Planning with CPO_

---

## 📝 QUESTIONS FOR CEO

Things I need clarity on before commencing Sprint 1:

- [ ] **Auth Scope**: Should MVP ship with mock auth or basic login? (Current: mock only)
- [ ] **Cognitive Layer**: Is NL query feature in or out of MVP scope?
- [ ] **Export Priority**: How important is BPMN/PNML export for MVP demo?
- [ ] **Test Coverage**: Acceptable minimum for shipping? (Current: low)
- [ ] **Demo Data**: Should we include sample datasets for demo purposes?

---

## 🔍 DEEP-DIVE: Discovery Flow Analysis

### What Works (53% Coverage)

1. ✅ All miner algorithms functional (Alpha, Inductive, Heuristics, ILP, etc.)
2. ✅ DFG visualization with frequency/performance annotations
3. ✅ Petri net generation and conversion
4. ✅ Activity statistics and footprints
5. ✅ Variant extraction and ranking
6. ✅ Start/end activity detection

### What's Missing (Blocking 100%)

1. ❌ **Export to BPMN/PNML** — Backend has capability, UI not wired
2. ❌ **Algorithm parameter configuration** — Hardcoded defaults
3. ❌ **Model comparison** — No side-by-side view
4. ❌ **Share discovery results** — No sharing service
5. ❌ **Model annotations persistence** — Ephemeral only

### Recommendation for MVP

Focus on **visual proof of mining**: User uploads CSV → sees process graph. Export/share can be Sprint 2.

---

## 🔍 DEEP-DIVE: Ingestion Flow Analysis

### What Works (90% Coverage)

1. ✅ CSV and XES file upload
2. ✅ Column auto-detection
3. ✅ Preview with sample data
4. ✅ Manual column mapping (case_id, activity, timestamp)
5. ✅ Processing and storage
6. ✅ Dataset appears in project list

### What Might Need Polish

1. ⚠️ Error handling for malformed files
2. ⚠️ Large file progress feedback
3. ⚠️ Duplicate detection
4. ⚠️ Character encoding issues

### Recommendation for MVP

Should be **demo-ready with happy path**. Edge case handling can follow.

---

_Document generated by CTO Agent for ATLAS Platform_
