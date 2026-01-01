# Database Documentation

This document provides a comprehensive overview of the database structure used in the Process Miner application. The schema is defined using DBML (Database Markup Language), which can be visualized at [dbdiagram.io](https://dbdiagram.io).

## DBML Schema File

The full schema definition can be found in [database_schema.dbml](file:///Users/namanagarwal/system/docs/database_schema.dbml).

## Architectural Layers

The database is organized into several key layers:

### 1. Organization Layer

- **projects**: Container for organizing event logs and analyses.

### 2. Event Log Layer (Traditional)

- **event_logs**: Metadata and statistics for uploaded event logs.
- **uploaded_files**: Tracking of the physical files associated with logs.
- **process_cases**: Individual traces/cases within a log.
- **process_events**: Discrete events tied to specific cases.

### 3. Analysis & Modeling

- **analyses**: Saved configurations and results of process analyses.
- **process_models**: Discovered models (Petri nets, DFGs) stored as serialized objects.
- **conformance_results**: Alignment and fitness metrics between logs and models.

### 4. OCEL 2.0 (Object-Centric)

Modern standard for process mining where events can relate to multiple objects.

- **ocel2_events**: Events with many-to-many relationships to objects.
- **ocel2_objects**: Business entities (Orders, Items, etc.).
- **ocel2_e2o_relations**: Event-to-Object links.
- **ocel2_o2o_relations**: Object-to-Object links.
- **ocel2_object_attribute_changes**: Temporal tracking of object state.

### 5. Automation & Prediction

- **workflows**: Pipeline definitions for automated analysis.
- **async_jobs**: Lifecycle tracking for background tasks.
- **prediction_models**: ML models for outcome prediction.
- **recommendations**: Prescriptive actions based on analysis results.

## Usage

To visualize this schema:

1. Copy the contents of `database_schema.dbml`.
2. Paste them into the editor at [dbdiagram.io](https://dbdiagram.io).
