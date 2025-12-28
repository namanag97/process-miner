# Phased Development Roadmap

## Development Phases Overview

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#7C3AED', 'secondaryColor': '#10B981', 'tertiaryColor': '#F59E0B'}}}%%
flowchart LR
    subgraph PHASE1["🟢 Phase 1: Core Foundation"]
        direction TB
        P1_LOG["Event Log<br/>Management"]
        P1_CASE["Case & Event<br/>Processing"]
        P1_VAR["Variant<br/>Analysis"]
        P1_ACT["Activity<br/>Types"]
    end

    subgraph PHASE2["🔵 Phase 2: Process Discovery"]
        direction TB
        P2_MODEL["Process Model<br/>Repository"]
        P2_DISC["Discovery<br/>Algorithms"]
        P2_DFG["DFG & Petri<br/>Net Storage"]
        P2_QUAL["Model Quality<br/>Metrics"]
    end

    subgraph PHASE3["🟡 Phase 3: Conformance"]
        direction TB
        P3_REF["Reference<br/>Models"]
        P3_CHECK["Conformance<br/>Checking"]
        P3_DEV["Deviation<br/>Analysis"]
        P3_COMP["Compliance<br/>Rules"]
    end

    subgraph PHASE4["🟠 Phase 4: Performance"]
        direction TB
        P4_PERF["Performance<br/>Analysis"]
        P4_BOTTLE["Bottleneck<br/>Detection"]
        P4_KPI["KPI<br/>Management"]
        P4_SLA["SLA<br/>Monitoring"]
    end

    subgraph PHASE5["🔴 Phase 5: Dashboards"]
        direction TB
        P5_DASH["Dashboard<br/>Builder"]
        P5_VIZ["Visualizations"]
        P5_REPORT["Reports &<br/>Exports"]
    end

    PHASE1 --> PHASE2 --> PHASE3 --> PHASE4 --> PHASE5

    classDef phase1 fill:#10B981,stroke:#059669,color:#fff
    classDef phase2 fill:#6366F1,stroke:#4F46E5,color:#fff
    classDef phase3 fill:#F59E0B,stroke:#D97706,color:#fff
    classDef phase4 fill:#F97316,stroke:#EA580C,color:#fff
    classDef phase5 fill:#EF4444,stroke:#DC2626,color:#fff

    class P1_LOG,P1_CASE,P1_VAR,P1_ACT phase1
    class P2_MODEL,P2_DISC,P2_DFG,P2_QUAL phase2
    class P3_REF,P3_CHECK,P3_DEV,P3_COMP phase3
    class P4_PERF,P4_BOTTLE,P4_KPI,P4_SLA phase4
    class P5_DASH,P5_VIZ,P5_REPORT phase5
```

---

## Phase Summary

| Phase | Focus                                      | Storage                        | Status      |
| ----- | ------------------------------------------ | ------------------------------ | ----------- |
| **1** | Event Log, Cases, Variants, Activities     | PostgreSQL `eventlog` schema   | ✅ Complete |
| **2** | Process Models, Discovery, DFG, Petri Nets | PostgreSQL `model` schema + S3 | ✅ Complete |
| **3** | Conformance, Deviations, Compliance Rules  | PostgreSQL `analysis` schema   | ✅ Complete |
| **4** | Performance, Bottlenecks, KPIs, SLAs       | PostgreSQL + ClickHouse        | ✅ Complete |
| **5** | Dashboards, Reports, Visualizations        | PostgreSQL + S3                | 🔮 Future   |

---

## Storage Architecture (Simplified)

```mermaid
%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#7C3AED'}}}%%
flowchart TB
    subgraph APP["Application Layer"]
        API["FastAPI Backend"]
    end

    subgraph PRIMARY["Primary Storage"]
        PG["PostgreSQL<br/>────<br/>Event Logs, Models<br/>Conformance, Analysis"]
    end

    subgraph ANALYTICS["Analytics (Phase 4+)"]
        CH["ClickHouse<br/>────<br/>Time-series KPIs<br/>Aggregated Metrics"]
    end

    subgraph CACHE["Cache Layer"]
        RD["Redis<br/>────<br/>Sessions, Cache<br/>Job Queues"]
    end

    subgraph FILES["Object Storage"]
        S3["S3/MinIO<br/>────<br/>Raw Uploads<br/>Model Files, Exports"]
    end

    API --> PG
    API --> RD
    API -.-> CH
    PG -.->|"Sync"| CH
    API --> S3

    classDef primary fill:#6366F1,stroke:#4F46E5,color:#fff
    classDef analytics fill:#EF4444,stroke:#DC2626,color:#fff
    classDef cache fill:#F97316,stroke:#EA580C,color:#fff
    classDef files fill:#A855F7,stroke:#9333EA,color:#fff

    class PG primary
    class CH analytics
    class RD cache
    class S3 files
```

---

## Changelog

| Date       | Version | Changes                                                                                      |
| ---------- | ------- | -------------------------------------------------------------------------------------------- |
| 2024-12-28 | 0.5.0   | **API Layer Complete**: 14 new endpoints for all 3 flows (ingestion, discovery, conformance) |
| 2024-12-28 | 0.4.0   | **Phase 2-4 ERD Complete**: Added 25 ORM models (8 discovery, 8 conformance, 9 performance)  |
| 2024-12-28 | 0.3.0   | Phase 2 partial: `Transition`, `ResourceProfile`, model versioning                           |
| 2024-12-28 | 0.2.0   | Value objects: `LogStatistics`, `QualityReport`, `FilterConfig`                              |
| 2024-12-28 | 0.1.0   | Core: `EventLog`, `ProcessCase`, `ProcessEvent`, `ProcessModel`                              |

---

## Current State (v0.5.0)

### ✅ Backend Ready

| Component                | Status | Details                                              |
| ------------------------ | ------ | ---------------------------------------------------- |
| **Event Log Ingestion**  | ✅     | CSV/XES upload, preview, statistics, quality reports |
| **Process Discovery**    | ✅     | Alpha, Inductive, Heuristics, DFG miners via PM4Py   |
| **Conformance Checking** | ✅     | Token Replay, Alignments, deviation patterns         |
| **API Layer**            | ✅     | 27 endpoints across 3 routers                        |
| **Domain Model**         | ✅     | DDD with entities, value objects, aggregates         |
| **ORM Models**           | ✅     | 25 SQLAlchemy models                                 |

### 🔜 Frontend Pending

| Component          | Status | Next Step                        |
| ------------------ | ------ | -------------------------------- |
| **Dashboard UI**   | 🔜     | Build React/Next.js frontend     |
| **Visualizations** | 🔜     | D3/React Flow for process graphs |
| **Reports**        | 🔜     | PDF/CSV export functionality     |

### API Endpoints Summary

```
/api/v1/logs        → 11 routes (upload, preview, stats, quality, variants)
/api/v1/discovery   →  8 routes (miners, discover, DFG, Petri net, model quality)
/api/v1/conformance →  8 routes (check, alignments, patterns, quality metrics)
```

See [routers/README.md](../backend/src/presentation/api/routers/README.md) for endpoint details.

---

## Deferred for Scale

The following capabilities are intentionally deferred:

- **Multi-tenancy** (tenant isolation, workspaces) → Enterprise phase
- **Predictive Analytics** (ML models, anomaly detection) → AI phase
- **Automation Workflows** (triggers, orchestration) → Automation phase
- **Advanced Search** (Elasticsearch integration) → Scale phase

---

_See [extracted_erd.md](./extracted_erd.md) for detailed entity definitions._
