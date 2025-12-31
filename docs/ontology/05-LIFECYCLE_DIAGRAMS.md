# Lifecycle Diagrams — Birth-to-Death Flows for Each Entity

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Overview

This document describes the lifecycle of each domain entity from creation through modification to archival/destruction.

---

## EventLog Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVENT LOG LIFECYCLE                                │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │  File Upload │
                              │  (CSV/XES)   │
                              └──────┬───────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   COLUMN DETECTION    │
                         │  (detect_columns)     │
                         └───────────┬───────────┘
                                     │
                           User confirms mapping
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      INGESTION        │
                         │  Creates EventLog,    │
                         │  ProcessCases,        │
                         │  ProcessEvents        │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE STATE                                     │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                  │
│  │ Process Mining │  │   Analytics    │  │  Predictions   │                  │
│  └───────┬────────┘  └───────┬────────┘  └───────┬────────┘                  │
│          │                   │                   │                            │
│          ▼                   ▼                   ▼                            │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐                  │
│  │ Discover Model │  │ Detect Bottle- │  │ Train Predictor│                  │
│  │ Check Conform- │  │ necks, Rework, │  │ Make Predictions│                 │
│  │ ance...        │  │ Cycle Time...  │  │                │                  │
│  └────────────────┘  └────────────────┘  └────────────────┘                  │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────┐                 │
│  │                      FILTERING                          │                 │
│  │  Creates NEW EventLog (is_filtered=true)               │                 │
│  │  Original log remains UNCHANGED                        │                 │
│  │  Filtered log references source_log_id                 │                 │
│  └─────────────────────────────────────────────────────────┘                 │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────┐                 │
│  │                  PROJECT ASSOCIATION                    │                 │
│  │  Can be added to/removed from projects                 │                 │
│  │  project_id is MUTABLE (SET NULL)                      │                 │
│  └─────────────────────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ User deletes
                                     ▼
                         ┌───────────────────────┐
                         │      DELETION         │
                         │  CASCADE deletes:     │
                         │  - All ProcessCases   │
                         │  - All ProcessEvents  │
                         │  - Filtered logs      │
                         │  - AnalyticsCache     │
                         │  - SocialNetworks     │
                         │  - PredictionModels   │
                         │                       │
                         │  SET NULL on:         │
                         │  - ProcessModels      │
                         │  - Project reference  │
                         └───────────────────────┘
```

### EventLog State Table

| State              | Entry Condition    | Exit Conditions           | Valid Operations                 |
| ------------------ | ------------------ | ------------------------- | -------------------------------- |
| **Pending Upload** | File selected      | Ingestion started         | Column detection                 |
| **Ingesting**      | Ingestion started  | Ingestion complete/failed | None (blocking)                  |
| **Active**         | Ingestion complete | Deletion                  | All analytics, filtering, mining |
| **Deleted**        | User/system delete | Terminal                  | None                             |

---

## ProcessModel Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PROCESS MODEL LIFECYCLE                              │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────────┐
                         │   Discovery Request   │
                         │  (log_id, miner_type) │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   MINING EXECUTION    │
                         │  PM4Py algorithm runs │
                         │  Model serialized     │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE STATE                                     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  CONFORMANCE CHECKING                                                   │  │
│  │  - Token Replay → fitness score                                        │  │
│  │  - Alignment → fitness + precision                                     │  │
│  │  → Creates ConformanceResult                                           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  VISUALIZATION                                                          │  │
│  │  - Get Petri Net structure                                             │  │
│  │  - Render SVG                                                          │  │
│  │  - Extract JSON for frontend                                           │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  SIMULATION                                                             │  │
│  │  - Play-out (generate synthetic log)                                   │  │
│  │  - What-if scenarios                                                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Quality Metrics Updated:                                                    │
│  - fitness (computed on conformance check)                                  │
│  - precision (computed on conformance check)                                │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Source EventLog deleted
                                     │ OR Manual deletion
                                     ▼
                         ┌───────────────────────┐
                         │      ORPHANED         │
                         │  log_id = NULL        │
                         │  Model still usable   │
                         │  for visualization    │
                         └───────────────────────┘
                                     │
                                     │ Manual deletion
                                     ▼
                         ┌───────────────────────┐
                         │      DELETED          │
                         │  CASCADE deletes:     │
                         │  - ConformanceResults │
                         └───────────────────────┘
```

---

## Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WORKFLOW LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────────┐
                         │  From Template        │
                         │    OR                 │
                         │  Custom Definition    │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │      CREATION         │
                         │  Validate steps       │
                         │  Set is_active=true   │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE STATE                                     │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                         EXECUTION                                      │   │
│  │                                                                        │   │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐           │   │
│  │   │ Step 1  │───▶│ Step 2  │───▶│ Step 3  │───▶│ Step N  │           │   │
│  │   │ (ingest)│    │(discover)│   │(conform)│    │ (stats) │           │   │
│  │   └─────────┘    └─────────┘    └─────────┘    └─────────┘           │   │
│  │        │               │              │              │                │   │
│  │        └───────────────┴──────────────┴──────────────┘                │   │
│  │                              │                                         │   │
│  │                     Creates WorkflowRun                               │   │
│  │                     (tracks execution state)                          │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
│  Updateable:                                                                 │
│  - name                                                                      │
│  - steps_json                                                                │
│  - schedule                                                                  │
│  - is_active (enable/disable)                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────┐             ┌───────────────────┐
        │    DEACTIVATED    │             │     DELETED       │
        │  is_active=false  │             │  CASCADE deletes: │
        │  Still exists     │             │  - All WorkflowRuns│
        │  Can reactivate   │             │                   │
        └───────────────────┘             └───────────────────┘
```

---

## WorkflowRun Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW RUN LIFECYCLE                                │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────────┐
                         │   Run Triggered       │
                         │  (manual or schedule) │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       PENDING         │
                         │  status="pending"     │
                         │  started_at=null      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │       RUNNING         │
                         │  status="running"     │
                         │  started_at=now()     │
                         │  Executing steps...   │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────┐             ┌───────────────────┐
        │    COMPLETED      │             │      FAILED       │
        │ status="completed"│             │  status="failed"  │
        │ completed_at=now()│             │  error="..."      │
        │ result_json={...} │             │  completed_at=now()│
        └───────────────────┘             └───────────────────┘
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                                     ▼ (Terminal states)

```

---

## PredictionModel Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PREDICTION MODEL LIFECYCLE                             │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────────┐
                         │   Training Request    │
                         │ (log_id, target_type, │
                         │  algorithm)           │
                         └───────────┬───────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │ Sync Mode              Async Mode│
                    ▼                                 ▼
        ┌───────────────────┐             ┌───────────────────┐
        │   TRAINING        │             │   TRAINING        │
        │  (blocking)       │             │  via AsyncJob     │
        │  Extract features │             │  status="pending" │
        │  Train model      │             │  → "running"      │
        │  Evaluate metrics │             │  → "completed"    │
        └─────────┬─────────┘             └─────────┬─────────┘
                  │                                 │
                  └────────────────┬────────────────┘
                                   │
                                   ▼
                         ┌───────────────────────┐
                         │       TRAINED         │
                         │  model_binary set     │
                         │  metrics_json set     │
                         │  trained_at set       │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE STATE                                     │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  PREDICTION                                                             │  │
│  │  - Single prediction (case_prefix → next_activity/remaining_time)      │  │
│  │  - Batch prediction (multiple prefixes)                                │  │
│  │  - Returns confidence scores and alternatives                          │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Model is IMMUTABLE after training                                           │
│  To retrain: create NEW PredictionModel                                      │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Source EventLog deleted
                                     │ OR Manual deletion
                                     ▼
                         ┌───────────────────────┐
                         │      DELETED          │
                         │  CASCADE from log     │
                         │  OR manual delete     │
                         └───────────────────────┘
```

---

## Project Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PROJECT LIFECYCLE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌───────────────────────┐
                         │      CREATION         │
                         │  name (required)      │
                         │  description (opt)    │
                         │  tags (opt)           │
                         └───────────┬───────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              ACTIVE STATE                                     │
│                                                                               │
│  Updateable fields:                                                          │
│  - name                                                                      │
│  - description                                                               │
│  - tags                                                                      │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │  FILE MANAGEMENT                                                        │  │
│  │  - Add EventLog to project (set log.project_id)                        │  │
│  │  - Remove EventLog from project (set log.project_id = NULL)            │  │
│  │  - total_files counter updated                                         │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Statistics tracked:                                                         │
│  - total_files (event logs count)                                           │
│  - total_analyses (usage counter)                                           │
└──────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ User deletes
                                     ▼
                         ┌───────────────────────┐
                         │      DELETED          │
                         │  EventLogs PRESERVED  │
                         │  (project_id → NULL)  │
                         │  No cascade delete    │
                         └───────────────────────┘
```

---

## Summary: Object Lifecycle Matrix

| Entity                | Creation                | Modification             | Archival                  | Destruction                                 |
| --------------------- | ----------------------- | ------------------------ | ------------------------- | ------------------------------------------- |
| **Project**           | User creates            | Name, description, tags  | N/A                       | User deletes (logs preserved)               |
| **EventLog**          | File upload + ingestion | Project association only | N/A                       | User/cascade deletes (cascades to children) |
| **ProcessCase**       | Auto during ingestion   | Never                    | N/A                       | Cascade from EventLog                       |
| **ProcessEvent**      | Auto during ingestion   | Never                    | N/A                       | Cascade from ProcessCase                    |
| **ProcessModel**      | Discovery execution     | Quality metrics          | Orphaned when log deleted | Manual/cascade delete                       |
| **ConformanceResult** | Conformance check       | Never (point-in-time)    | N/A                       | Cascade from log/model                      |
| **Workflow**          | User creates            | Steps, schedule, active  | Deactivated               | User deletes (cascades runs)                |
| **WorkflowRun**       | Workflow execution      | Status progression       | Terminal states           | Cascade from Workflow                       |
| **PredictionModel**   | Training request        | Never (immutable)        | N/A                       | Manual/cascade delete                       |
| **SocialNetwork**     | On-demand discovery     | Never (regenerate)       | N/A                       | Cascade from EventLog                       |
| **AnalyticsCache**    | On-demand compute       | Refresh on TTL           | N/A                       | TTL expiry / cascade                        |
| **AsyncJob**          | Long-running op start   | Status, progress         | Completed/Failed          | Manual cleanup                              |
