# Process Mining Platform - System Architecture Document (SAD)
## NASA-Style Hierarchical Decomposition

---

## Document Control

| Item | Value |
|------|-------|
| Document ID | PMP-SAD-001 |
| Version | 1.0.0 |
| Classification | Enterprise SaaS Architecture |
| Standard | NASA-STD-8739.8 / ISO/IEC 42010 |

---

## 1. System Hierarchy Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    PROCESS MINING PLATFORM (L0 - MISSION)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   GROUND    │ │    DATA     │ │  PROCESSING │ │INTELLIGENCE │ │ MISSION   │ │
│  │   SEGMENT   │ │   SEGMENT   │ │   SEGMENT   │ │   SEGMENT   │ │ CONTROL   │ │
│  │    (GS)     │ │    (DS)     │ │    (PS)     │ │    (IS)     │ │   (MC)    │ │
│  │   L1-100    │ │   L1-200    │ │   L1-300    │ │   L1-400    │ │  L1-500   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Segment Breakdown

### L1-100: GROUND SEGMENT (GS) - Core Infrastructure
```
L1-100 GROUND SEGMENT
├── L2-110 Identity & Access Management System (IAMS)
│   ├── L3-111 Authentication Subsystem
│   ├── L3-112 Authorization Subsystem
│   └── L3-113 Session Management Subsystem
│
├── L2-120 Tenant Management System (TMS)
│   ├── L3-121 Organization Subsystem
│   ├── L3-122 User Management Subsystem
│   └── L3-123 Team & Permission Subsystem
│
└── L2-130 Audit & Compliance System (ACS)
    ├── L3-131 Audit Logging Subsystem
    ├── L3-132 Compliance Rules Subsystem
    └── L3-133 Data Retention Subsystem
```

### L1-200: DATA SEGMENT (DS) - Data Infrastructure
```
L1-200 DATA SEGMENT
├── L2-210 Event Log Management System (ELMS)
│   ├── L3-211 Traditional Event Log Subsystem (XES/CSV)
│   ├── L3-212 Case Management Subsystem
│   └── L3-213 Activity Registry Subsystem
│
├── L2-220 Object-Centric Event Log System (OCELS)
│   ├── L3-221 OCEL Core Subsystem
│   ├── L3-222 Object Graph Subsystem
│   └── L3-223 OCEL Flattening Subsystem
│
├── L2-230 Data Connector System (DCS)
│   ├── L3-231 Database Connector Subsystem
│   ├── L3-232 Enterprise System Connector Subsystem (SAP, Camunda)
│   ├── L3-233 Productivity Connector Subsystem (Outlook, GitHub)
│   ├── L3-234 Desktop Connector Subsystem (Browser, Windows)
│   └── L3-235 Sync Management Subsystem
│
└── L2-240 Data Quality System (DQS)
    ├── L3-241 Validation Subsystem
    ├── L3-242 Filtering Subsystem
    └── L3-243 Privacy Subsystem (PRIPEL, SaCoFa)
```

### L1-300: PROCESSING SEGMENT (PS) - Computation Engine
```
L1-300 PROCESSING SEGMENT
├── L2-310 Process Discovery System (PDS)
│   ├── L3-311 Procedural Discovery Subsystem (Alpha, Heuristics, Inductive, ILP)
│   ├── L3-312 Declarative Discovery Subsystem (DECLARE, Log Skeleton)
│   ├── L3-313 DFG Discovery Subsystem
│   └── L3-314 Advanced Discovery Subsystem (POWL, Temporal Profile)
│
├── L2-320 Process Model System (PMS)
│   ├── L3-321 Petri Net Subsystem
│   ├── L3-322 BPMN Subsystem
│   ├── L3-323 Process Tree Subsystem
│   ├── L3-324 POWL Subsystem
│   └── L3-325 DFG Model Subsystem
│
├── L2-330 Conformance Checking System (CCS)
│   ├── L3-331 Token Replay Subsystem
│   ├── L3-332 Alignment Subsystem
│   ├── L3-333 Declarative Conformance Subsystem
│   ├── L3-334 Temporal Conformance Subsystem
│   └── L3-335 Footprint Subsystem
│
├── L2-340 Analysis & Metrics System (AMS)
│   ├── L3-341 Soundness Analysis Subsystem
│   ├── L3-342 Simplicity Metrics Subsystem
│   ├── L3-343 Variant Analysis Subsystem
│   ├── L3-344 Performance Metrics Subsystem
│   └── L3-345 Batch Detection Subsystem
│
└── L2-350 Simulation System (SS)
    ├── L3-351 Playout Subsystem
    └── L3-352 Stochastic Simulation Subsystem
```

### L1-400: INTELLIGENCE SEGMENT (IS) - AI & Analytics
```
L1-400 INTELLIGENCE SEGMENT
├── L2-410 Machine Learning System (MLS)
│   ├── L3-411 Feature Engineering Subsystem
│   ├── L3-412 Model Training Subsystem
│   └── L3-413 Prediction Subsystem
│
├── L2-420 LLM Integration System (LIS)
│   ├── L3-421 LLM Session Subsystem
│   ├── L3-422 Log Abstraction Subsystem
│   └── L3-423 Hypothesis Generation Subsystem
│
└── L2-430 Social Network Analysis System (SNAS)
    ├── L3-431 Network Analysis Subsystem
    └── L3-432 Organizational Mining Subsystem
```

### L1-500: MISSION CONTROL (MC) - Operations & Presentation
```
L1-500 MISSION CONTROL
├── L2-510 Automation System (AS)
│   ├── L3-511 Trigger Subsystem
│   ├── L3-512 Action Execution Subsystem
│   └── L3-513 Workflow Orchestration Subsystem
│
├── L2-520 Alert & Notification System (ANS)
│   ├── L3-521 Alert Management Subsystem
│   ├── L3-522 Incident Management Subsystem
│   └── L3-523 Notification Delivery Subsystem
│
├── L2-530 Reporting System (RS)
│   ├── L3-531 Report Generation Subsystem
│   ├── L3-532 Export Subsystem
│   └── L3-533 Scheduling Subsystem
│
├── L2-540 Visualization System (VS)
│   ├── L3-541 Process Visualization Subsystem
│   ├── L3-542 Analytics Visualization Subsystem
│   └── L3-543 Interactive Exploration Subsystem
│
└── L2-550 Collaboration System (CS)
    ├── L3-551 Dashboard Subsystem
    ├── L3-552 Commentary Subsystem
    └── L3-553 Annotation Subsystem
```

---

## 3. Interface Control Document (ICD) Summary

### Critical Interfaces

| Interface ID | From System | To System | Data Flow | Protocol |
|--------------|-------------|-----------|-----------|----------|
| IF-001 | IAMS (L2-110) | ALL | Auth Tokens | JWT/OAuth2 |
| IF-002 | ELMS (L2-210) | PDS (L2-310) | Event Logs | Internal API |
| IF-003 | ELMS (L2-210) | CCS (L2-330) | Event Logs | Internal API |
| IF-004 | PDS (L2-310) | PMS (L2-320) | Process Models | PNML/BPMN |
| IF-005 | PMS (L2-320) | CCS (L2-330) | Process Models | Internal API |
| IF-006 | DCS (L2-230) | ELMS (L2-210) | Raw Events | Batch/Stream |
| IF-007 | OCELS (L2-220) | ELMS (L2-210) | Flattened Logs | Internal API |
| IF-008 | AMS (L2-340) | VS (L2-540) | Metrics | JSON |
| IF-009 | MLS (L2-410) | AS (L2-510) | Predictions | Internal API |
| IF-010 | LIS (L2-420) | External LLM | Prompts/Responses | REST API |
| IF-011 | ANS (L2-520) | External | Notifications | SMTP/Webhook |
| IF-012 | ACS (L2-130) | ALL | Audit Events | Event Bus |

---

## 4. File Structure

```
/dbml
├── 00_enums/
│   └── enums.dbml                    # All enumeration types
│
├── L1-100_ground_segment/
│   ├── L2-110_identity_access.dbml   # IAMS
│   ├── L2-120_tenant_management.dbml # TMS
│   └── L2-130_audit_compliance.dbml  # ACS
│
├── L1-200_data_segment/
│   ├── L2-210_event_log.dbml         # ELMS
│   ├── L2-220_ocel.dbml              # OCELS
│   ├── L2-230_connectors.dbml        # DCS
│   └── L2-240_data_quality.dbml      # DQS
│
├── L1-300_processing_segment/
│   ├── L2-310_discovery.dbml         # PDS
│   ├── L2-320_process_models.dbml    # PMS
│   ├── L2-330_conformance.dbml       # CCS
│   ├── L2-340_analysis_metrics.dbml  # AMS
│   └── L2-350_simulation.dbml        # SS
│
├── L1-400_intelligence_segment/
│   ├── L2-410_machine_learning.dbml  # MLS
│   ├── L2-420_llm_integration.dbml   # LIS
│   └── L2-430_social_network.dbml    # SNAS
│
├── L1-500_mission_control/
│   ├── L2-510_automation.dbml        # AS
│   ├── L2-520_alerts.dbml            # ANS
│   ├── L2-530_reporting.dbml         # RS
│   ├── L2-540_visualization.dbml     # VS
│   └── L2-550_collaboration.dbml     # CS
│
└── interfaces/
    └── interface_tables.dbml         # Cross-system reference tables
```

---

## 5. PM4Py Module Mapping

| PM4Py Module | System ID | System Name |
|--------------|-----------|-------------|
| `pm4py.read` / `pm4py.write` | L2-210 | Event Log Management System |
| `pm4py.convert` | L2-210, L2-320 | ELMS, Process Model System |
| `pm4py.ocel` | L2-220 | Object-Centric Event Log System |
| `pm4py.connectors` | L2-230 | Data Connector System |
| `pm4py.filtering` | L2-242 | Filtering Subsystem |
| `pm4py.privacy` | L2-243 | Privacy Subsystem |
| `pm4py.discovery` | L2-310 | Process Discovery System |
| `pm4py.conformance` | L2-330 | Conformance Checking System |
| `pm4py.analysis` | L2-340 | Analysis & Metrics System |
| `pm4py.stats` | L2-340 | Analysis & Metrics System |
| `pm4py.sim` | L2-350 | Simulation System |
| `pm4py.ml` | L2-410 | Machine Learning System |
| `pm4py.llm` | L2-420 | LLM Integration System |
| `pm4py.org` | L2-430 | Social Network Analysis System |
| `pm4py.vis` | L2-540 | Visualization System |

---

## 6. Deployment View

```
┌────────────────────────────────────────────────────────────────────────────┐
│                           KUBERNETES CLUSTER                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  GROUND SEGMENT  │  │   DATA SEGMENT   │  │PROCESSING SEGMENT│         │
│  │    Namespace     │  │    Namespace     │  │    Namespace     │         │
│  │                  │  │                  │  │                  │         │
│  │ • Auth Service   │  │ • Event Service  │  │ • Discovery Svc  │         │
│  │ • Tenant Service │  │ • OCEL Service   │  │ • Conformance Svc│         │
│  │ • Audit Service  │  │ • Connector Svc  │  │ • Analysis Svc   │         │
│  │                  │  │ • Quality Svc    │  │ • Simulation Svc │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                            │
│  ┌──────────────────┐  ┌──────────────────┐                               │
│  │INTELLIGENCE SEG. │  │ MISSION CONTROL  │                               │
│  │    Namespace     │  │    Namespace     │                               │
│  │                  │  │                  │                               │
│  │ • ML Service     │  │ • Automation Svc │                               │
│  │ • LLM Gateway    │  │ • Alert Service  │                               │
│  │ • SNA Service    │  │ • Report Service │                               │
│  │                  │  │ • Dashboard Svc  │                               │
│  └──────────────────┘  └──────────────────┘                               │
│                                                                            │
├────────────────────────────────────────────────────────────────────────────┤
│                           SHARED SERVICES                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ PostgreSQL │ │   Redis    │ │   Kafka    │ │    MinIO   │              │
│  │  Cluster   │ │  Cluster   │ │  Cluster   │ │  (S3-like) │              │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

*Document generated following NASA Systems Engineering Handbook (NASA/SP-2016-6105)*
