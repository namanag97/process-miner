# Process Mining SaaS - Database Schema

**Schema-Driven Architecture**: Define once → Generate SQLAlchemy models, Pydantic schemas, TypeScript types, API docs

---

## Architecture

```
Admin Domain → Datasets Domain → Analysis Domain
      ↓              ↓                   ↓
      └──────────────┴───────────────────┘
                     ↓
         Platform Infrastructure
```

---

## DBML Schema

```dbml
//// Admin Domain - Multi-tenant hierarchy ////

Table organizations {
  id varchar(36) [pk]
  name varchar(255) [not null]
  slug varchar(100) [not null, unique]
  plan varchar(50) [not null, default: 'free']
  created_at datetime [not null, default: `now()`]
  updated_at datetime

  indexes {
    slug [unique]
  }
}

Table users {
  id varchar(36) [pk]
  org_id varchar(36) [ref: > organizations.id]
  email varchar(255) [not null, unique]
  name varchar(255)
  auth_provider varchar(50) [not null, default: 'local']
  auth_provider_id varchar(255)
  role varchar(50) [not null, default: 'member']
  password_hash varchar(255)
  created_at datetime [not null, default: `now()`]
  last_login_at datetime

  indexes {
    email [unique]
    org_id
  }
}

Table workspaces {
  id varchar(36) [pk]
  org_id varchar(36) [not null, ref: > organizations.id]
  name varchar(255) [not null]
  description text
  created_at datetime [not null, default: `now()`]
  updated_at datetime
}

Table workspace_members {
  id varchar(36) [pk]
  workspace_id varchar(36) [not null, ref: > workspaces.id]
  user_id varchar(36) [not null, ref: > users.id]
  role varchar(20) [not null, default: 'member'] // owner, admin, member, viewer
  joined_at datetime [not null, default: `now()`]

  indexes {
    (workspace_id, user_id) [unique]
  }
}

Table projects {
  id varchar(36) [pk]
  workspace_id varchar(36) [ref: > workspaces.id]
  name varchar(255) [not null]
  description text
  tags_json text
  total_files int [not null, default: 0]
  total_analyses int [not null, default: 0]
  created_at datetime [not null, default: `now()`]
  updated_at datetime
}

//// Platform Infrastructure ////

Table async_jobs {
  id varchar(36) [pk]
  task_id varchar(255) [unique]
  user_id varchar(36)
  job_type varchar(50) [not null]
  status varchar(20) [not null, default: 'pending']
  progress int [not null, default: 0]
  stage varchar(100)
  entity_type varchar(50)
  entity_id varchar(36)
  parent_job_id varchar(36) [ref: > async_jobs.id]
  parameters_json text
  result_json text
  error text
  error_message text
  created_at datetime [not null, default: `now()`]
  started_at datetime
  completed_at datetime
  updated_at datetime

  indexes {
    task_id [unique]
    user_id
    job_type
    status
    entity_type
    entity_id
  }
}

Table error_logs {
  id varchar(36) [pk]
  timestamp datetime [not null, default: `now()`]
  level varchar(20) [not null]
  exception_type varchar(255) [not null]
  exception_message text [not null]
  stack_trace text
  request_id varchar(36)
  user_id varchar(36)
  endpoint varchar(255)
  method varchar(10)
  context_json text
  resolved bool [not null, default: false]
  resolved_at datetime
  resolved_by varchar(36)
  notes text

  indexes {
    timestamp
    level
    user_id
    resolved
  }
}

//// Datasets Domain - Event log lifecycle ////

Table datasets {
  id varchar(36) [pk]
  name varchar(255) [not null]
  source_file varchar(500)
  source_format varchar(20) [not null, default: 'csv']
  project_id varchar(36) [ref: > projects.id]

  // Statistics
  total_cases int [not null, default: 0]
  total_events int [not null, default: 0]
  total_activities int [not null, default: 0]

  // JSON metadata
  activities_json text
  statistics_json text

  // Lifecycle
  status varchar(20) [not null, default: 'pending']
  error_message text
  mapping_json text
  column_suggestions_json text
  detected_columns_json text

  // File metadata
  file_size_bytes int
  storage_key varchar(500)

  // Job tracking
  validation_job_id varchar(36) [ref: > async_jobs.id]
  ingestion_job_id varchar(36) [ref: > async_jobs.id]

  // Filtering
  source_dataset_id varchar(36) [ref: > datasets.id]
  filter_config_json text
  is_filtered bool [not null, default: false]
  filter_stats_json text

  created_at datetime [not null, default: `now()`]
  updated_at datetime

  indexes {
    status
    project_id
  }
}

Table dataset_columns {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  name varchar(255) [not null]
  dtype varchar(50) [not null] // STRING, INTEGER, DATETIME, FLOAT
  position int [not null]

  // Statistics for mapping UI
  sample_values_json text
  null_count int [not null, default: 0]
  null_percentage float [not null, default: 0.0]
  unique_count int [not null, default: 0]

  // ML suggestions
  suggested_role varchar(50) // case_id, activity, timestamp, resource
  suggestion_confidence float // 0.0-1.0

  created_at datetime [not null, default: `now()`]

  indexes {
    dataset_id
    (dataset_id, position) [unique]
  }
}

Table dataset_column_mappings {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, unique, ref: - datasets.id]

  // Required mappings
  case_id_column varchar(255) [not null]
  activity_column varchar(255) [not null]
  timestamp_column varchar(255) [not null]

  // Optional mappings
  timestamp_format varchar(100)
  resource_column varchar(255)

  // Additional columns
  additional_columns_json text
  confidence_scores_json text
  auto_mapped bool [not null, default: false]

  created_at datetime [not null, default: `now()`]
  updated_at datetime
}

Table dataset_metadata {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, unique, ref: - datasets.id]

  // Core counts
  total_events int [not null, default: 0]
  total_cases int [not null, default: 0]
  total_activities int [not null, default: 0]
  total_variants int [not null, default: 0]

  // Time range
  first_event_at datetime
  last_event_at datetime

  // Duration stats (seconds)
  avg_case_duration float
  min_case_duration float
  max_case_duration float

  // Resource stats
  total_resources int

  // Computation tracking
  computed_at datetime [not null, default: `now()`]
  computation_time_ms int
}

Table uploaded_files {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, unique, ref: - datasets.id]
  filename varchar(500) [not null]
  storage_path varchar(1000) [not null]
  size_bytes int
  mime_type varchar(100)
  checksum varchar(64)
  created_at datetime [not null, default: `now()`]
}

//// Lookup Tables - Normalized string values ////

Table lookup_activities {
  id int [pk, increment]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  name varchar(255) [not null]

  indexes {
    dataset_id
    (dataset_id, name) [unique]
  }
}

Table lookup_resources {
  id int [pk, increment]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  name varchar(255) [not null]

  indexes {
    dataset_id
    (dataset_id, name) [unique]
  }
}

//// Analysis Domain - Process mining and analytics ////

Table process_cases {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  case_id varchar(255) [not null]
  variant_key text
  start_time datetime
  end_time datetime

  indexes {
    dataset_id
    case_id
    variant_key
  }
}

Table process_events {
  id varchar(36) [pk]
  case_ref_id varchar(36) [not null, ref: > process_cases.id]

  // Normalized references
  activity_id int [ref: > lookup_activities.id]
  resource_id int [ref: > lookup_resources.id]

  // Denormalized for DuckDB analytics
  activity varchar(255) [not null]
  resource varchar(255)

  timestamp datetime [not null]
  attributes_json text

  indexes {
    case_ref_id
    activity_id
    (case_ref_id, timestamp)
    (activity_id, timestamp)
    (timestamp, activity_id)
  }
}

Table process_models {
  id varchar(36) [pk]
  name varchar(255) [not null]
  dataset_id varchar(36) [ref: > datasets.id]
  miner_type varchar(50) [not null]
  model_format varchar(50) [not null]
  serialized_model blob
  standard_content_path varchar(500)
  graph_structure_json text
  metadata_json text
  fitness float
  precision float
  created_at datetime [not null, default: `now()`]
}

Table process_model_metrics {
  id varchar(36) [pk]
  model_id varchar(36) [not null, ref: - process_models.id]
  total_activities int
  total_transitions int
  complexity_score float
  fitness_score float
  precision_score float
  computed_at datetime [not null, default: `now()`]
  created_at datetime [not null, default: `now()`]
  updated_at datetime [not null, default: `now()`]
}

Table graph_cache {
  id varchar(36) [pk]
  model_id varchar(36) [not null, ref: > process_models.id]
  abstraction_level int [not null, default: 0]
  layout_algorithm varchar(50) [not null, default: 'dagre']
  cached_layout_json text
  expires_at datetime
  created_at datetime [not null, default: `now()`]
  updated_at datetime [not null, default: `now()`]
}

Table analyses {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  name varchar(255) [not null]
  analysis_type varchar(50) [not null]
  config_json text
  status varchar(20) [not null, default: 'pending']
  error_message text
  result_summary_json text
  result_json text
  model_id varchar(36) [ref: > process_models.id]
  created_at datetime [not null, default: `now()`]
  completed_at datetime
}

Table conformance_results {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  model_id varchar(36) [not null, ref: > process_models.id]
  fitness float [not null]
  precision float
  method varchar(50) [not null, default: 'token_replay']
  generalization float
  simplicity float
  f_score float
  non_fitting_traces int
  average_alignment_cost float
  diagnostics_json text
  created_at datetime [not null, default: `now()`]
}

Table analytics_cache {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  metric_type varchar(50) [not null]
  result_json text
  computed_at datetime [not null, default: `now()`]
  ttl_seconds int [not null, default: 3600]
}

Table prediction_models {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  target_type varchar(50) [not null]
  algorithm varchar(50) [not null]
  model_binary blob
  metrics_json text
  trained_at datetime [not null, default: `now()`]
}

Table predictions {
  id varchar(36) [pk]
  model_id varchar(36) [not null, ref: > prediction_models.id]
  case_prefix_json text
  prediction_json text
  confidence float
  predicted_at datetime [not null, default: `now()`]
}

Table recommendations {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  case_id varchar(255) [not null]
  signal_type varchar(50) [not null]
  signal_data_json text
  action_type varchar(50) [not null]
  action_params_json text
  priority varchar(20) [not null, default: 'medium']
  state varchar(20) [not null, default: 'pending']
  created_at datetime [not null, default: `now()`]
}

//// Object-Centric Process Mining (OCEL 1.0) ////

Table ocel_logs {
  id varchar(36) [pk]
  name varchar(255) [not null]
  source_file varchar(500)
  source_format varchar(20) [not null, default: 'jsonocel']
  total_events int [not null, default: 0]
  total_objects int [not null, default: 0]
  total_object_types int [not null, default: 0]
  metadata_json text
  ocel_data blob // deferred loading
  created_at datetime [not null, default: `now()`]
}

Table ocel_object_types {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > ocel_logs.id]
  name varchar(255) [not null]
  object_count int [not null, default: 0]
  attributes_schema_json text

  indexes {
    dataset_id
  }
}

Table oc_petri_nets {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > ocel_logs.id]
  name varchar(255) [not null]
  object_types_json text
  serialized_model blob // deferred loading
  created_at datetime [not null, default: `now()`]

  indexes {
    dataset_id
  }
}

//// OCEL 2.0 Standard ////

Table ocel2_event_types {
  id varchar(36) [pk]
  name varchar(255) [not null, unique]
  attributes_schema json
}

Table ocel2_object_types {
  id varchar(36) [pk]
  name varchar(255) [not null, unique]
  attributes_schema json
}

Table ocel2_events {
  id varchar(36) [pk]
  event_type_id varchar(36) [not null, ref: > ocel2_event_types.id]
  activity varchar(255) [not null]
  timestamp datetime [not null]
  attributes json
  source_dataset_id varchar(36) [ref: > datasets.id]
  created_at datetime [not null, default: `now()`]

  indexes {
    activity
    timestamp
  }
}

Table ocel2_objects {
  id varchar(36) [pk]
  object_type_id varchar(36) [not null, ref: > ocel2_object_types.id]
  object_id varchar(255) [not null]
  attributes json
  created_at datetime [not null, default: `now()`]

  indexes {
    object_id
  }
}

Table ocel2_e2o_relations {
  id varchar(36) [pk]
  event_id varchar(36) [not null, ref: > ocel2_events.id]
  object_id varchar(36) [not null, ref: > ocel2_objects.id]
  qualifier varchar(50) [not null, default: 'involved']

  indexes {
    event_id
    object_id
  }
}

Table ocel2_o2o_relations {
  id varchar(36) [pk]
  source_object_id varchar(36) [not null, ref: > ocel2_objects.id]
  target_object_id varchar(36) [not null, ref: > ocel2_objects.id]
  qualifier varchar(50) [not null]
  attributes json
  created_at datetime [not null, default: `now()`]

  indexes {
    source_object_id
    target_object_id
  }
}

Table ocel2_object_attribute_changes {
  id varchar(36) [pk]
  object_id varchar(36) [not null, ref: > ocel2_objects.id]
  event_id varchar(36) [ref: > ocel2_events.id]
  attribute_name varchar(255) [not null]
  old_value text
  new_value text
  changed_at datetime [not null, default: `now()`]

  indexes {
    object_id
  }
}

//// Organizational Mining ////

Table social_networks {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  network_type varchar(50) [not null]
  graph_json text
  metrics_json text
  created_at datetime [not null, default: `now()`]
}

Table activity_mappings {
  id varchar(36) [pk]
  dataset_id varchar(36) [not null, ref: > datasets.id]
  name varchar(200) [not null]
  description text
  level int [not null, default: 0]
  mapping_rules text [not null]
  created_at datetime [not null, default: `now()`]
  updated_at datetime [not null, default: `now()`]
}

Table hierarchical_process_models {
  id varchar(36) [pk]
  mapping_id varchar(36) [not null, ref: > activity_mappings.id]
  level int [not null]
  graph_structure_json text [not null]
  pnml_path varchar(500)
  activity_count int [not null]
  edge_count int [not null]
  created_at datetime [not null, default: `now()`]
  updated_at datetime [not null, default: `now()`]
}

//// Workflows & Automation ////

Table workflows {
  id varchar(36) [pk]
  name varchar(255) [not null]
  steps_json text [not null]
  schedule varchar(100)
  is_active bool [not null, default: true]
  created_at datetime [not null, default: `now()`]
  updated_at datetime
}

Table workflow_runs {
  id varchar(36) [pk]
  workflow_id varchar(36) [not null, ref: > workflows.id]
  dataset_id varchar(36) [ref: > datasets.id]
  status varchar(50) [not null, default: 'pending']
  result_json text
  error text
  started_at datetime
  completed_at datetime
}
```

---

## Entity Relationships

### Admin Hierarchy
```
Organization (1) ──< (N) Workspaces
Organization (1) ──< (N) Users
Workspace (1) ──< (N) WorkspaceMembers >── (1) User
Workspace (1) ──< (N) Projects
```

### Dataset Lifecycle
```
Project (1) ──< (N) Datasets
Dataset (1) ─── (1) UploadedFile
Dataset (1) ──< (N) DatasetColumns
Dataset (1) ─── (1) DatasetColumnMapping
Dataset (1) ─── (1) DatasetMetadata
Dataset (1) ──< (N) Activity (lookup)
Dataset (1) ──< (N) Resource (lookup)
```

### Analysis Flow
```
Dataset (1) ──< (N) ProcessCases
ProcessCase (1) ──< (N) ProcessEvents
ProcessEvent (N) ──> (1) Activity (lookup)
ProcessEvent (N) ──> (1) Resource (lookup)

Dataset (1) ──< (N) ProcessModels
ProcessModel (1) ─── (1) ProcessModelMetrics
ProcessModel (1) ──< (N) GraphCache

Dataset (1) ──< (N) Analyses
Analysis (N) ──> (1) ProcessModel

Dataset (1) ──< (N) ConformanceResults
ConformanceResult (N) ──> (1) ProcessModel

Dataset (1) ──< (N) PredictionModels
PredictionModel (1) ──< (N) Predictions
Dataset (1) ──< (N) Recommendations
```

### OCEL 1.0 (Object-Centric)
```
OCELLog (1) ──< (N) OCELObjectType
OCELLog (1) ──< (N) OCPetriNet
```

### OCEL 2.0 Standard
```
OCEL2EventType (1) ──< (N) OCEL2Event
OCEL2ObjectType (1) ──< (N) OCEL2Object

OCEL2Event (1) ──< (N) E2ORelation >── (N) OCEL2Object
OCEL2Object (1) ──< (N) O2ORelation >── (N) OCEL2Object (self-referential)

OCEL2Object (1) ──< (N) ObjectAttributeChange
OCEL2Event (1) ──< (N) ObjectAttributeChange
```

### Organizational Mining
```
Dataset (1) ──< (N) SocialNetwork
Dataset (1) ──< (N) ActivityMapping
ActivityMapping (1) ──< (N) HierarchicalProcessModel
```

### Workflows
```
Workflow (1) ──< (N) WorkflowRun
WorkflowRun (N) ──> (1) Dataset
```

---

## Key Design Patterns

### 1. UUID Primary Keys
All domain entities use `varchar(36)` UUIDs for:
- Distributed ID generation
- No coordination required
- Frontend-friendly

### 2. Soft Deletes via CASCADE
Foreign keys use `ondelete="CASCADE"` or `ondelete="SET NULL"` for referential integrity.

### 3. JSON Columns
Flexible metadata stored as JSON text:
- `activities_json`: Activity frequency distributions
- `statistics_json`: Dataset summary stats
- `result_json`: Analysis results
- `*_json`: Additional semi-structured data

### 4. Normalized Lookups
`lookup_activities` and `lookup_resources` normalize high-cardinality strings:
- Storage: 4-byte int vs 255-byte varchar
- Query perf: Integer JOIN > String comparison
- Denormalized copies (`activity`, `resource`) for DuckDB analytics

### 5. Status Tracking
All async operations tracked via:
- `status` field (pending, running, completed, failed)
- `error_message` for failures
- Foreign key to `async_jobs` table

### 6. Timestamp Patterns
- `created_at`: Entity creation
- `updated_at`: Last modification
- `completed_at`: Task completion
- `computed_at`: Cache generation

### 7. OCEL 2.0 Architecture
Multi-dimensional event logs supporting:
- **E2O Relations**: Events relate to multiple objects (many-to-many)
- **O2O Relations**: Objects relate to other objects (graph structure)
- **Qualified Relationships**: Roles like "created", "modified", "part_of"
- **Attribute History**: Track object attribute changes over time
- **Type Systems**: Schema validation via `attributes_schema` JSON

### 8. Hierarchical Abstraction
Activity mappings enable multi-level process views:
- Level 0: Raw activities
- Level 1+: Aggregated/abstracted activities
- Each level generates separate process models
- Supports drill-down from high-level to detailed views

---

## Migration Strategy

Current state: **SQLAlchemy models** (source of truth)

### Phase 1: Schema Extraction
- [x] Document existing SQLAlchemy models
- [x] Generate DBML representation
- [ ] Validate all relationships

### Phase 2: Schema-First Design
- [ ] Create single source DBML schema
- [ ] Generate SQLAlchemy models from DBML
- [ ] Generate Pydantic schemas from DBML
- [ ] Generate TypeScript types from DBML
- [ ] Auto-update OpenAPI spec

### Phase 3: Tooling
- [ ] Pre-commit hook to validate schema changes
- [ ] CI/CD schema diff checker
- [ ] Migration generator from DBML changes

---

## Statistics

- **Total Tables**: 48
- **Admin Domain**: 5 tables
- **Platform Infra**: 2 tables
- **Datasets Domain**: 6 tables
- **Lookup Tables**: 2 tables
- **Analysis Domain**: 15 tables
- **OCEL 1.0**: 3 tables
- **OCEL 2.0**: 7 tables
- **Organizational Mining**: 3 tables
- **Workflows**: 2 tables
- **Predictive**: 3 tables

**Foreign Keys**: 70+ relationships
**Indexes**: 50+ indexes for query optimization

## Notes

**DevConsole**: Real-time observability models (Pydantic schemas, not persisted to DB)
- `DevLogEntry`: Enhanced log entry with metadata
- `SystemMetrics`: Real-time metrics snapshot
- `HeartbeatMessage`: Periodic system state

These are in-memory models for live debugging, not part of the database schema.
