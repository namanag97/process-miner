# Process Mining Platform - NASA-Style DBML Schema

## Overview

This repository contains a **NASA-style hierarchical database schema** for an Enterprise Process Mining & Business Automation SaaS platform with full **PM4Py integration**.

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PROCESS MINING PLATFORM (L0 - MISSION)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  L1-100          L1-200          L1-300          L1-400          L1-500         │
│  GROUND          DATA            PROCESSING      INTELLIGENCE    MISSION        │
│  SEGMENT         SEGMENT         SEGMENT         SEGMENT         CONTROL        │
│                                                                                 │
│  • Identity      • Event Logs    • Discovery     • ML            • Automation   │
│  • Tenants       • OCEL 2.0      • Models        • LLM           • Alerts       │
│  • Audit         • Connectors    • Conformance   • SNA           • Dashboards   │
│                  • Quality       • Analysis                      • Reports      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
dbml/
├── 00_ARCHITECTURE.md              # System architecture document
├── 00_enums/
│   └── enums.dbml                  # All enumeration types (735 lines)
│
├── L1-100_ground_segment/          # Core Infrastructure
│   ├── L2-110_identity_access.dbml # Authentication, Authorization, Sessions
│   ├── L2-120_tenant_management.dbml # Organizations, Users, Teams
│   └── L2-130_audit_compliance.dbml  # Audit logs, Compliance, Retention
│
├── L1-200_data_segment/            # Data Infrastructure
│   ├── L2-210_event_log.dbml       # Event logs, Cases, Activities, Variants
│   ├── L2-220_ocel.dbml            # OCEL 2.0, Object graphs, Flattening
│   ├── L2-230_connectors.dbml      # Database, SAP, Camunda, GitHub, etc.
│   └── L2-240_data_quality.dbml    # Validation, Filtering, Privacy
│
├── L1-300_processing_segment/      # Computation Engine
│   ├── L2-310_discovery.dbml       # All discovery algorithms
│   ├── L2-320_process_models.dbml  # Petri nets, BPMN, Process trees, POWL
│   ├── L2-330_conformance.dbml     # Token replay, Alignments, DECLARE
│   └── L2-340_350_analysis_simulation.dbml # Analysis, Metrics, Simulation
│
├── L1-400_intelligence_segment/    # AI & Analytics
│   ├── L2-410_420_ml_llm.dbml      # ML features, models, LLM integration
│   └── L2-430_social_network.dbml  # SNA, Organizational mining
│
├── L1-500_mission_control/         # Operations & Presentation
│   ├── L2-510_520_automation_alerts.dbml # Automations, Alerts, Incidents
│   └── L2-530_540_550_reporting_viz_collab.dbml # Reports, Dashboards, Collaboration
│
└── interfaces/
    └── interface_tables.dbml       # Cross-system reference tables
```

## Statistics

| Segment | Systems | Tables | Lines |
|---------|---------|--------|-------|
| Shared Enums | - | 72 enums | 735 |
| L1-100 Ground | 3 | ~25 | 1,477 |
| L1-200 Data | 4 | ~35 | 1,854 |
| L1-300 Processing | 4 | ~40 | 1,912 |
| L1-400 Intelligence | 3 | ~20 | 884 |
| L1-500 Mission Control | 5 | ~25 | 1,227 |
| Interfaces | - | ~10 | 534 |
| **TOTAL** | **19** | **~155 tables** | **8,914** |

## PM4Py Module Coverage

| PM4Py Module | System(s) | Tables |
|--------------|-----------|--------|
| `pm4py.read` / `pm4py.write` | L2-210 ELMS | event_logs, events, cases |
| `pm4py.convert` | L2-210, L2-320 | model_conversions |
| `pm4py.ocel` | L2-220 OCELS | ocel_logs, ocel_objects, ocel_events, ocel_object_graphs |
| `pm4py.connectors` | L2-230 DCS | connectors, connector_*_config, sync_jobs |
| `pm4py.filtering` | L2-240 DQS | saved_filters, filtered_event_logs |
| `pm4py.privacy` | L2-240 DQS | privacy_configs, privacy_jobs |
| `pm4py.discovery` | L2-310 PDS | discovery_jobs, declare_models, log_skeletons, temporal_profiles |
| `pm4py.conformance` | L2-330 CCS | conformance_checks, alignment_results, token_replay_results |
| `pm4py.analysis` | L2-340 AMS | soundness_analyses, simplicity_metrics, emd_comparisons |
| `pm4py.stats` | L2-340 AMS | process_metrics, batch_detections, self_distance_results |
| `pm4py.sim` | L2-350 SS | simulation_configs, simulation_runs, stochastic_petri_nets |
| `pm4py.ml` | L2-410 MLS | ml_datasets, ml_features, ml_models, ml_predictions |
| `pm4py.llm` | L2-420 LIS | llm_sessions, llm_messages, llm_abstractions, llm_hypotheses |
| `pm4py.org` | L2-430 SNAS | sna_analyses, sna_resources, organizational_roles |
| `pm4py.vis` | L2-540 VS | saved_visualizations, dashboard_widgets |

## Usage with dbdiagram.io

1. Go to [dbdiagram.io](https://dbdiagram.io)
2. Create a new diagram
3. Copy and paste the contents of each `.dbml` file
4. Start with `00_enums/enums.dbml` then add system files

## Key Design Patterns

- **Multi-tenancy**: All tables include `org_id` foreign key
- **Soft deletes**: `deleted_at` timestamp instead of hard delete
- **Audit trail**: Comprehensive audit logging via L2-130
- **Event-driven**: Interface tables for cross-system communication
- **CQRS-ready**: Separation of command and query patterns
- **Saga pattern**: Long-running process tracking

## Generated Following

- NASA Systems Engineering Handbook (NASA/SP-2016-6105)
- ISO/IEC 42010 Systems Architecture Standard
- DBML (Database Markup Language) Specification

---
*Schema Version: 1.0.0 | Generated: 2026-01-01*
