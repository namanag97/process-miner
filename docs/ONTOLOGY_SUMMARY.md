# Ontological Analysis — Executive Summary

> **ATLAS (Automated Taxonomy & Logical Architecture Specialist)**  
> System: Process Mining SaaS Platform  
> Generated: 2025-12-31

---

## Quick Navigation

| Document                                                            | Description                              |
| ------------------------------------------------------------------- | ---------------------------------------- |
| [01-OBJECT_CATALOG.md](./ontology/01-OBJECT_CATALOG.md)             | Complete inventory of all domain objects |
| [02-ATTRIBUTE_DICTIONARY.md](./ontology/02-ATTRIBUTE_DICTIONARY.md) | All properties across all objects        |
| [03-GLOSSARY.md](./ontology/03-GLOSSARY.md)                         | Business definitions for domain terms    |
| [04-IDENTITY_REGISTRY.md](./ontology/04-IDENTITY_REGISTRY.md)       | Object identification patterns           |
| [05-LIFECYCLE_DIAGRAMS.md](./ontology/05-LIFECYCLE_DIAGRAMS.md)     | Birth-to-death flows                     |
| [06-STATE_MACHINES.md](./ontology/06-STATE_MACHINES.md)             | State transition specifications          |

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PROCESS MINING SAAS PLATFORM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐         │
│  │    FRONTEND     │    │     BACKEND     │    │    DATABASE     │         │
│  │   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (SQLite)      │         │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘         │
│         │                       │                                           │
│         │                       │                                           │
│  ┌──────▼──────┐         ┌──────▼──────┐                                   │
│  │ SDK Modules │         │   PM4Py     │                                   │
│  │ (11 total)  │         │  Services   │                                   │
│  └─────────────┘         │ (10 total)  │                                   │
│                          └─────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Domain Model Summary

### Core Entities (16 ORM Tables)

```
┌─────────────────────────────────────────────────────────────────┐
│                     AGGREGATE ROOTS                              │
├─────────────────────────────────────────────────────────────────┤
│  Project          → Container for organizing work              │
│  EventLog         → Uploaded process data                      │
│  OCELLog          → Object-centric event log                   │
│  Workflow         → Automation pipeline definition             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CHILD ENTITIES                              │
├─────────────────────────────────────────────────────────────────┤
│  ProcessCase      → Process instance (case/trace)              │
│  ProcessEvent     → Individual activity occurrence             │
│  ProcessModel     → Discovered process representation          │
│  ConformanceResult→ Log-model conformance metrics              │
│  WorkflowRun      → Workflow execution instance                │
│  OCELObjectType   → Object type in OCEL                        │
│  OCPetriNet       → Object-centric process model               │
│  PredictionModel  → ML predictor for process outcomes          │
│  SocialNetwork    → Organizational network graph               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE ENTITIES                        │
├─────────────────────────────────────────────────────────────────┤
│  AnalyticsCache   → Cached computation results (TTL)           │
│  AsyncJob         → Long-running operation tracking            │
│  Prediction       → Individual prediction record               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Relationships

```
Project ─────────────────┐
    └──owns──► EventLog ─┼──owns──► ProcessCase ──owns──► ProcessEvent
                         │
                         ├──derives──► EventLog (filtered)
                         │
                         ├──produces─► ProcessModel ──checked──► ConformanceResult
                         │
                         ├──trains───► PredictionModel
                         │
                         └──analyzes─► SocialNetwork
                                       AnalyticsCache
```

---

## Service Architecture

| Service                   | Domain            | Key Operations                     |
| ------------------------- | ----------------- | ---------------------------------- |
| **IngestionService**      | Data Foundation   | CSV/XES parsing, column detection  |
| **MiningService**         | Process Discovery | 6 mining algorithms, DFG, variants |
| **ConformanceService**    | Quality Analysis  | Token replay, alignment checking   |
| **AnalyticsService**      | Performance       | Bottlenecks, rework, cycle time    |
| **OrganizationalService** | Resources         | Social networks, role discovery    |
| **PredictionService**     | AI/ML             | Next activity, remaining time      |
| **SimulationService**     | What-If           | Play-out, capacity planning        |
| **FilteringService**      | Data Prep         | Time/variant/activity filters      |
| **OCPMService**           | Object-Centric    | OCEL processing, OC-DFG            |
| **WorkflowService**       | Automation        | Pipeline orchestration             |

---

## Frontend SDK Modules

| Module           | API Mapping                                      |
| ---------------- | ------------------------------------------------ |
| `projects`       | `/api/v1/projects/*`                             |
| `processes`      | `/api/v1/processes/*`                            |
| `discovery`      | `/api/v1/discovery/*`, `/api/v1/visualization/*` |
| `analytics`      | `/api/v1/analytics/*`                            |
| `conformance`    | `/api/v1/conformance/*`                          |
| `predictions`    | `/api/v1/predictions/*`                          |
| `organizational` | `/api/v1/organizational/*`                       |
| `simulation`     | `/api/v1/simulation/*`                           |
| `audit`          | `/api/v1/audit/*`                                |
| `ai`             | AI assistant integration                         |

---

## State Machines

| Entity          | States                               | Type              |
| --------------- | ------------------------------------ | ----------------- |
| **WorkflowRun** | pending → running → completed/failed | System-controlled |
| **AsyncJob**    | pending → running → completed/failed | System-controlled |
| **Workflow**    | active ↔ deactivated → deleted       | User-controlled   |
| **EventLog**    | ingesting → active → deleted         | Mixed             |
| **User Auth**   | unauthenticated ↔ authenticated      | Mixed             |

---

## Identity Patterns

- **All entities**: UUID primary keys (surrogate)
- **ProcessCase**: Composite key (log_id + case_id from source)
- **Variants**: Natural key (activity sequence hash)
- **DFG Elements**: Computed IDs from activity names

---

## Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ CSV/XES     │────►│  Ingestion  │────►│  EventLog   │
│ File Upload │     │  Service    │     │  + Cases    │
└─────────────┘     └─────────────┘     │  + Events   │
                                        └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
            │   Discovery   │          │   Analytics   │          │  Predictions  │
            │   Service     │          │   Service     │          │   Service     │
            └───────┬───────┘          └───────┬───────┘          └───────┬───────┘
                    │                          │                          │
                    ▼                          ▼                          ▼
            ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
            │ ProcessModel  │          │ Performance   │          │ PredictionModel│
            │ DFG, Variants │          │ Metrics, KPIs │          │ ML Models     │
            └───────────────┘          └───────────────┘          └───────────────┘
```

---

## Quality Standards Met

| Criterion        | Status | Evidence                                  |
| ---------------- | ------ | ----------------------------------------- |
| **Complete**     | ✅     | All 16 ORM entities documented            |
| **Precise**      | ✅     | Exact types, constraints, enums specified |
| **Hierarchical** | ✅     | Clear parent-child relationships mapped   |
| **Traceable**    | ✅     | Source file locations included            |
| **Actionable**   | ✅     | Can generate diagrams, validation code    |
| **Versioned**    | ✅     | Generated 2025-12-31                      |

---

## Recommendations

1. **Consider explicit state fields**: EventLog processing states are implicit; adding a `status` field would improve observability.

2. **Add soft delete**: Currently using hard deletes; soft delete (archived flag) would preserve audit trails.

3. **Standardize timestamps**: Some entities have `created_at` only, others have both `created_at` and `updated_at`. Consider standardizing.

4. **Add tenant isolation**: For multi-tenant SaaS, add `tenant_id` to aggregate roots.

5. **Document event sourcing**: The system tracks snapshots, not events. Consider event sourcing for audit requirements.

---

## Files Generated

```
/Users/namanagarwal/system/docs/
├── ONTOLOGY_SUMMARY.md          (this file)
└── ontology/
    ├── 01-OBJECT_CATALOG.md     (178 lines)
    ├── 02-ATTRIBUTE_DICTIONARY.md (490 lines)
    ├── 03-GLOSSARY.md           (450 lines)
    ├── 04-IDENTITY_REGISTRY.md  (330 lines)
    ├── 05-LIFECYCLE_DIAGRAMS.md (350 lines)
    └── 06-STATE_MACHINES.md     (400 lines)
```

Total documentation: ~2,200 lines of structured ontological analysis.
