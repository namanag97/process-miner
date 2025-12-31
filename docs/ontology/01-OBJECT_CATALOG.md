# Object Catalog — Complete Inventory

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Overview

This document provides a complete inventory of all domain objects discovered in the codebase, classified by their type, scope, persistence, and cardinality.

```
Total Backend ORM Entities:    16
Total Backend Pydantic Schemas: 90+
Total Backend Enums:           5
Total Backend Services:        10
Total Frontend SDK Modules:    11
Total Frontend Types:          25+
```

---

## Phase 1: Object Identification

### 1.1 Core Domain Objects (Backend ORM)

| Object                | Type           | Scope          | Persistence | Cardinality | Source           |
| --------------------- | -------------- | -------------- | ----------- | ----------- | ---------------- |
| **Project**           | Aggregate Root | Domain         | Persistent  | Collection  | `orm.py:25-47`   |
| **EventLog**          | Entity         | Domain         | Persistent  | Collection  | `orm.py:54-111`  |
| **ProcessCase**       | Entity         | Domain         | Persistent  | Collection  | `orm.py:114-139` |
| **ProcessEvent**      | Entity         | Domain         | Persistent  | Collection  | `orm.py:142-159` |
| **ProcessModel**      | Entity         | Domain         | Persistent  | Collection  | `orm.py:162-187` |
| **ConformanceResult** | Entity         | Domain         | Persistent  | Collection  | `orm.py:190-211` |
| **Workflow**          | Aggregate Root | Application    | Persistent  | Collection  | `orm.py:214-237` |
| **WorkflowRun**       | Entity         | Application    | Persistent  | Collection  | `orm.py:240-263` |
| **OCELLog**           | Aggregate Root | Domain         | Persistent  | Collection  | `orm.py:271-304` |
| **OCELObjectType**    | Entity         | Domain         | Persistent  | Collection  | `orm.py:307-323` |
| **OCPetriNet**        | Entity         | Domain         | Persistent  | Collection  | `orm.py:326-346` |
| **AnalyticsCache**    | Value Object   | Application    | Cached      | Collection  | `orm.py:354-366` |
| **SocialNetwork**     | Entity         | Domain         | Persistent  | Collection  | `orm.py:374-386` |
| **PredictionModel**   | Entity         | Domain         | Persistent  | Collection  | `orm.py:394-407` |
| **Prediction**        | Value Object   | Domain         | Persistent  | Collection  | `orm.py:410-422` |
| **AsyncJob**          | Entity         | Infrastructure | Persistent  | Collection  | `orm.py:430-442` |

---

### 1.2 Enumeration Types (Backend)

| Enum                  | Values                                                                          | Usage                                 |
| --------------------- | ------------------------------------------------------------------------------- | ------------------------------------- |
| **MinerType**         | `alpha`, `alpha_plus`, `inductive`, `inductive_infrequent`, `heuristics`, `dfg` | Process discovery algorithm selection |
| **ModelFormat**       | `petri_net`, `process_tree`, `dfg`, `bpmn`                                      | Process model representation format   |
| **SourceFormat**      | `csv`, `xes`, `ocel_json`, `ocel_sqlite`                                        | Event log source file format          |
| **ConformanceMethod** | `token_replay`, `alignment`                                                     | Conformance checking algorithm        |
| **WorkflowStatus**    | `pending`, `running`, `completed`, `failed`                                     | Workflow execution state              |

---

### 1.3 Frontend Domain Types

| Type                | Scope         | Related Backend Type         | Source                    |
| ------------------- | ------------- | ---------------------------- | ------------------------- |
| **EventLog**        | Domain        | ProcessResponse              | `transformers.ts:23-35`   |
| **Project**         | Domain        | ProjectResponse              | `projects.ts:7-16`        |
| **ProjectDetail**   | Domain        | ProjectDetailResponse        | `projects.ts:18-30`       |
| **DFGNode**         | Visualization | DFGNode                      | `transformers.ts:49-55`   |
| **DFGEdge**         | Visualization | DFGEdge                      | `transformers.ts:57-66`   |
| **DFGData**         | Visualization | DFGResponse                  | `transformers.ts:68-74`   |
| **Variant**         | Domain        | VariantResponse              | `transformers.ts:76-85`   |
| **ActivityDetail**  | Domain        | ActivityDetailResponse       | `transformers.ts:87-99`   |
| **PerformanceData** | Analytics     | PerformanceDashboardResponse | `transformers.ts:101-130` |
| **ReworkData**      | Analytics     | ReworkListResponse           | `transformers.ts:132-142` |
| **ColumnDetection** | Application   | ColumnDetectionResponse      | `transformers.ts:37-47`   |
| **User**            | Identity      | — (mock/real auth)           | `AuthContext.tsx:3-9`     |

---

## Object Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOMAIN LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Project (Aggregate Root)                                                   │
│   ├── owns: EventLog[] (composition, cascade delete via SET NULL)           │
│   │                                                                          │
│   └── EventLog (Entity)                                                      │
│       ├── owns: ProcessCase[] (composition, CASCADE delete)                 │
│       │   └── owns: ProcessEvent[] (composition, CASCADE delete)            │
│       ├── references: ProcessModel[] (association, SET NULL)                │
│       ├── references: source_log (self-reference for filtered logs)         │
│       └── owns: filtered_logs[] (composition for derived logs)              │
│                                                                              │
│   ProcessModel (Entity)                                                      │
│   └── references: EventLog (source_log, SET NULL on delete)                 │
│                                                                              │
│   ConformanceResult (Entity)                                                 │
│   ├── references: EventLog (CASCADE delete)                                  │
│   └── references: ProcessModel (CASCADE delete)                              │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           OCEL LAYER                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   OCELLog (Aggregate Root)                                                   │
│   ├── owns: OCELObjectType[] (composition, CASCADE delete)                  │
│   └── owns: OCPetriNet[] (composition, CASCADE delete)                      │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                           APPLICATION LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Workflow (Aggregate Root)                                                  │
│   └── owns: WorkflowRun[] (composition, CASCADE delete)                     │
│                                                                              │
│   PredictionModel (Entity)                                                   │
│   ├── references: EventLog (CASCADE delete)                                  │
│   └── owns: Prediction[] (implied, not modeled)                             │
│                                                                              │
│   SocialNetwork (Entity)                                                     │
│   └── references: EventLog (CASCADE delete)                                  │
│                                                                              │
│   AnalyticsCache (Value Object)                                              │
│   └── references: EventLog (CASCADE delete)                                  │
│                                                                              │
│   AsyncJob (Entity) — standalone, no foreign keys                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Relationship Metadata

| Relationship                     | Cardinality | Cascade  | Navigation     | Loading            |
| -------------------------------- | ----------- | -------- | -------------- | ------------------ |
| Project → EventLog               | 1:N         | SET NULL | Bidirectional  | selectin           |
| EventLog → ProcessCase           | 1:N         | CASCADE  | Bidirectional  | selectin           |
| ProcessCase → ProcessEvent       | 1:N         | CASCADE  | Bidirectional  | selectin (ordered) |
| EventLog → ProcessModel          | 1:N         | SET NULL | Bidirectional  | selectin           |
| EventLog → source_log            | N:1         | CASCADE  | Bidirectional  | selectin           |
| OCELLog → OCELObjectType         | 1:N         | CASCADE  | Bidirectional  | selectin           |
| OCELLog → OCPetriNet             | 1:N         | CASCADE  | Bidirectional  | selectin           |
| Workflow → WorkflowRun           | 1:N         | CASCADE  | Bidirectional  | selectin           |
| PredictionModel → EventLog       | N:1         | CASCADE  | Unidirectional | —                  |
| ConformanceResult → EventLog     | N:1         | CASCADE  | Unidirectional | —                  |
| ConformanceResult → ProcessModel | N:1         | CASCADE  | Unidirectional | —                  |

---

## Service Mapping

| Service                   | Primary Entities                          | Capabilities                                                |
| ------------------------- | ----------------------------------------- | ----------------------------------------------------------- |
| **IngestionService**      | EventLog, ProcessCase, ProcessEvent       | CSV/XES parsing, column detection, log creation             |
| **MiningService**         | EventLog, ProcessModel                    | Process discovery (6 algorithms), DFG, variants, statistics |
| **ConformanceService**    | EventLog, ProcessModel, ConformanceResult | Token replay, alignment, diagnostics, deviations            |
| **AnalyticsService**      | EventLog (via PM4Py)                      | Bottlenecks, rework, cycle time, throughput, patterns       |
| **OrganizationalService** | EventLog (via PM4Py)/SocialNetwork        | Handover network, roles, resource profiles, workload        |
| **PredictionService**     | EventLog, PredictionModel                 | Next activity, remaining time ML predictions                |
| **SimulationService**     | ProcessModel                              | Play-out, what-if simulation, capacity planning             |
| **FilteringService**      | EventLog                                  | Time/variant/activity/performance filtering                 |
| **OCPMService**           | OCELLog, OCELObjectType, OCPetriNet       | Object-centric process mining                               |
| **WorkflowService**       | Workflow, WorkflowRun                     | Pipeline orchestration, templates                           |

---

## Next Documents

- [02-ATTRIBUTE_DICTIONARY.md](./02-ATTRIBUTE_DICTIONARY.md) — All properties across all objects
- [03-GLOSSARY.md](./03-GLOSSARY.md) — Business definitions for domain terms
- [04-IDENTITY_REGISTRY.md](./04-IDENTITY_REGISTRY.md) — How each object type is uniquely identified
- [05-LIFECYCLE_DIAGRAMS.md](./05-LIFECYCLE_DIAGRAMS.md) — Birth-to-death flows for each entity
- [06-STATE_MACHINES.md](./06-STATE_MACHINES.md) — Formal state transition tables
