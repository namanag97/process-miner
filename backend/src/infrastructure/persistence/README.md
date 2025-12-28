# Process Mining Platform - System Overview

> **TL;DR**: DDD-based process mining backend with FastAPI, PM4Py, and SQLAlchemy. 41 tables, 27 API endpoints. Backend complete, frontend pending.

---

## Quick Facts

| Aspect           | Details                                            |
| ---------------- | -------------------------------------------------- |
| **Stack**        | Python 3.13, FastAPI, SQLAlchemy (async), PM4Py    |
| **Architecture** | Domain-Driven Design (DDD) with Clean Architecture |
| **Database**     | SQLite (dev) / PostgreSQL (prod), 41 tables        |
| **Version**      | v0.5.0                                             |

---

## Project Structure

```
backend/
├── src/
│   ├── domain/           # Entities, Value Objects, Aggregates
│   │   ├── entities.py   # EventLog, ProcessCase, ProcessEvent, ProcessModel
│   │   ├── aggregates.py # EventLogAggregate, ProcessModelAggregate
│   │   ├── value_objects.py # 30+ value objects (Timestamp, Duration, etc.)
│   │   └── events.py     # Domain events
│   ├── application/      # Use cases and services
│   │   ├── core/         # Discovery, Conformance, Transition services
│   │   ├── support/      # Ingestion, Quality services
│   │   └── generic/      # Auth, Notifications
│   ├── infrastructure/   # Database, messaging, storage
│   │   └── persistence/
│   │       ├── models.py # 41 ORM models
│   │       └── repositories.py
│   └── presentation/     # API layer
│       └── api/routers/  # FastAPI routers
└── tests/
```

---

## Database Schema (41 Tables)

| Phase              | Tables                                                                                | Purpose              |
| ------------------ | ------------------------------------------------------------------------------------- | -------------------- |
| **Core**           | `event_logs`, `process_cases`, `process_events`, `activity_types`, `process_variants` | Event log storage    |
| **Discovery**      | `process_models`, `model_versions`, `discovery_runs`, `petri_net_*`, `dfg_edges`      | Process mining       |
| **Conformance**    | `reference_models`, `conformance_runs`, `alignments`, `deviations`, `compliance_*`    | Conformance checking |
| **Performance**    | `analysis_runs`, `*_metrics`, `bottlenecks`, `kpis`, `alerts`                         | KPIs & analytics     |
| **Infrastructure** | `background_jobs`, `domain_events`, `sla_*`                                           | System support       |

---

## API Endpoints (27 Routes)

### Event Logs (`/api/v1/logs`)

- `POST /upload` - Upload CSV/XES file
- `GET /` - List all logs
- `GET /{id}` - Get log details
- `GET /{id}/statistics` - Log statistics
- `GET /{id}/variants` - Process variants
- `GET /{id}/quality` - Quality report

### Discovery (`/api/v1/discovery`)

- `GET /algorithms` - List miners (Alpha, Inductive, Heuristics, DFG)
- `POST /discover` - Run discovery
- `GET /jobs/{id}` - Job status
- `GET /models/{id}/dfg` - Get DFG
- `GET /models/{id}/petri-net` - Get Petri net

### Conformance (`/api/v1/conformance`)

- `POST /check` - Run conformance check
- `GET /jobs/{id}` - Job status
- `GET /results/{id}/alignments` - Get alignments
- `GET /results/{id}/deviations` - Get deviations

---

## Key Domain Entities

```
EventLog (Aggregate Root)
├── ProcessCase[]
│   └── ProcessEvent[]
├── statistics: LogStatistics
└── state: EventLogState (draft→parsing→validating→ready)

ProcessModel (Aggregate Root)
├── format: petri_net | bpmn | process_tree | dfg
├── miner_type: alpha | inductive | heuristics | dfg
└── state: discovering→discovered→saved

ConformanceResult
├── fitness, precision, generalization
└── deviations: Deviation[]
```

---

## How to Run

```bash
cd backend
source .venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

**Health check**: `GET http://localhost:8001/health`

---

## File Locations

| Need            | File                                               |
| --------------- | -------------------------------------------------- |
| ORM Models      | `backend/src/infrastructure/persistence/models.py` |
| Domain Entities | `backend/src/domain/entities.py`                   |
| Value Objects   | `backend/src/domain/value_objects.py`              |
| API Routers     | `backend/src/presentation/api/routers/`            |
| ERD Details     | `docs/extracted_erd.md`                            |
| Roadmap         | `docs/phased_development.md`                       |

---

## Version History

| Version | Date       | Changes                           |
| ------- | ---------- | --------------------------------- |
| v0.5.0  | 2024-12-28 | API layer complete (27 endpoints) |
| v0.4.0  | 2024-12-28 | ERD complete (25 new ORM models)  |
| v0.3.0  | 2024-12-28 | Transitions, resources, SLAs      |
| v0.2.0  | 2024-12-28 | Value objects, state machines     |
| v0.1.0  | 2024-12-28 | Core domain entities              |
