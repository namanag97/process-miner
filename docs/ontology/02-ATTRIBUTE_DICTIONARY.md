# Attribute Dictionary — All Properties Across All Objects

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Backend ORM Entity Attributes

### Project

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 36, UUID format]
  default_value: auto-generated UUID
  semantic_meaning: Unique project identifier
  source: system_generated

name:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 255, min_length: 1]
  semantic_meaning: Human-readable project name
  source: user_input

description:
  type: primitive
  data_type: text
  nullability: optional
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 2000]
  semantic_meaning: Extended description of project purpose
  source: user_input

tags_json:
  type: composite
  data_type: JSON (string[])
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Categorization tags for organization
  source: user_input

total_files:
  type: computed
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  semantic_meaning: Count of event logs in project
  source: derived_from (EventLog count)

total_analyses:
  type: computed
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  semantic_meaning: Count of analyses performed
  source: derived_from (relationship counts)

created_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Project creation timestamp
  source: system_generated

updated_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Last modification timestamp
  source: system_generated
```

---

### EventLog

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique event log identifier
  source: system_generated

name:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 255]
  semantic_meaning: Display name for the event log
  source: user_input | derived_from (filename)

source_file:
  type: primitive
  data_type: string
  nullability: optional
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 500]
  semantic_meaning: Original filename that was uploaded
  source: user_input

source_format:
  type: reference
  data_type: enum (SourceFormat)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: "csv"
  semantic_meaning: File format of the source data
  source: derived_from (file extension)

project_id:
  type: reference
  data_type: string (FK → projects.id)
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Parent project association
  source: user_input

total_cases:
  type: computed
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  semantic_meaning: Number of unique process instances
  source: derived_from (ProcessCase count)

total_events:
  type: computed
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  semantic_meaning: Total number of events across all cases
  source: derived_from (ProcessEvent count)

total_activities:
  type: computed
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  semantic_meaning: Number of distinct activity types
  source: derived_from (unique activities)

activities_json:
  type: composite
  data_type: JSON (string[])
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: List of unique activity names
  source: derived_from (ProcessEvent.activity)

statistics_json:
  type: composite
  data_type: JSON (object)
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Pre-computed statistics for quick access
  source: derived_from (analysis)

source_log_id:
  type: reference
  data_type: string (FK → event_logs.id, self-reference)
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Parent log if this is a filtered derivative
  source: system_generated

filter_config_json:
  type: composite
  data_type: JSON (FilterConfig[])
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Filter configuration that created this log
  source: user_input

is_filtered:
  type: primitive
  data_type: boolean
  nullability: required
  mutability: immutable
  visibility: public
  default_value: false
  semantic_meaning: Whether this log is derived from filtering
  source: system_generated

filter_stats_json:
  type: composite
  data_type: JSON (FilterStatistics)
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Statistics comparing original vs filtered
  source: derived_from (filtering operation)

created_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Upload/creation timestamp
  source: system_generated

updated_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Last modification timestamp
  source: system_generated
```

---

### ProcessCase

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Internal case record identifier
  source: system_generated

log_id:
  type: reference
  data_type: string (FK → event_logs.id)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Parent event log
  source: derived_from (upload context)

case_id:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 255, indexed]
  semantic_meaning: Business case identifier from source data
  source: user_input (CSV column)

variant_key:
  type: primitive
  data_type: text
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Activity sequence hash for variant grouping
  source: derived_from (activity sequence)

start_time:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Timestamp of first event in case
  source: derived_from (min timestamp)

end_time:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Timestamp of last event in case
  source: derived_from (max timestamp)
```

---

### ProcessEvent

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique event identifier
  source: system_generated

case_ref_id:
  type: reference
  data_type: string (FK → process_cases.id)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Parent case
  source: derived_from (case matching)

activity:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 255, indexed]
  semantic_meaning: Activity/task name that occurred
  source: user_input (CSV column)

timestamp:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [indexed]
  semantic_meaning: When the event occurred
  source: user_input (CSV column)

resource:
  type: primitive
  data_type: string
  nullability: optional
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 255]
  semantic_meaning: Who/what performed the activity
  source: user_input (CSV column)

attributes_json:
  type: composite
  data_type: JSON (object)
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Additional event attributes
  source: user_input (extra CSV columns)
```

---

### ProcessModel

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique model identifier
  source: system_generated

name:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 255]
  semantic_meaning: Display name for the model
  source: user_input | derived_from (log + miner)

log_id:
  type: reference
  data_type: string (FK → event_logs.id)
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Source event log for discovery
  source: derived_from (discovery context)

miner_type:
  type: reference
  data_type: enum (MinerType)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Algorithm used for discovery
  source: user_input

model_format:
  type: reference
  data_type: enum (ModelFormat)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Representation format of the model
  source: derived_from (miner output)

serialized_model:
  type: primitive
  data_type: binary (LargeBinary)
  nullability: optional
  mutability: immutable
  visibility: private
  semantic_meaning: Pickled PM4Py model object
  source: system_generated

fitness:
  type: computed
  data_type: float
  nullability: optional
  mutability: mutable
  visibility: public
  validation_rules: [0.0 - 1.0]
  semantic_meaning: Model fitness score (replay-based)
  source: derived_from (conformance checking)

precision:
  type: computed
  data_type: float
  nullability: optional
  mutability: mutable
  visibility: public
  validation_rules: [0.0 - 1.0]
  semantic_meaning: Model precision score
  source: derived_from (conformance checking)

created_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Discovery timestamp
  source: system_generated
```

---

### Workflow

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique workflow identifier
  source: system_generated

name:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 255]
  semantic_meaning: Workflow display name
  source: user_input

steps_json:
  type: composite
  data_type: JSON (WorkflowStep[])
  nullability: required
  mutability: mutable
  visibility: public
  semantic_meaning: Ordered list of pipeline steps
  source: user_input

schedule:
  type: primitive
  data_type: string
  nullability: optional
  mutability: mutable
  visibility: public
  validation_rules: [max_length: 100, cron format]
  semantic_meaning: Cron expression for scheduled runs
  source: user_input

is_active:
  type: primitive
  data_type: boolean
  nullability: required
  mutability: mutable
  visibility: public
  default_value: true
  semantic_meaning: Whether workflow is enabled
  source: user_input

created_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Workflow creation timestamp
  source: system_generated

updated_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Last modification timestamp
  source: system_generated
```

---

### WorkflowRun

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique run identifier
  source: system_generated

workflow_id:
  type: reference
  data_type: string (FK → workflows.id)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Parent workflow definition
  source: derived_from (execution context)

log_id:
  type: reference
  data_type: string (FK → event_logs.id)
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Input event log for this run
  source: user_input

status:
  type: reference
  data_type: enum (WorkflowStatus)
  nullability: required
  mutability: mutable
  visibility: public
  default_value: "pending"
  semantic_meaning: Current execution state
  source: system_generated

result_json:
  type: composite
  data_type: JSON (object)
  nullability: optional
  mutability: append-only
  visibility: public
  semantic_meaning: Execution results by step
  source: system_generated

error:
  type: primitive
  data_type: text
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Error message if failed
  source: system_generated

started_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Execution start timestamp
  source: system_generated

completed_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Execution completion timestamp
  source: system_generated
```

---

### PredictionModel

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique predictor identifier
  source: system_generated

log_id:
  type: reference
  data_type: string (FK → event_logs.id)
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: Training data source
  source: derived_from (training context)

target_type:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 50, enum: next_activity|remaining_time|outcome]
  semantic_meaning: What the model predicts
  source: user_input

algorithm:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules:
    [max_length: 50, enum: random_forest|xgboost|gradient_boosting]
  semantic_meaning: ML algorithm used
  source: user_input

model_binary:
  type: primitive
  data_type: binary (LargeBinary)
  nullability: optional
  mutability: immutable
  visibility: private
  semantic_meaning: Pickled scikit-learn model
  source: system_generated

metrics_json:
  type: composite
  data_type: JSON ({accuracy?, mae?, rmse?})
  nullability: optional
  mutability: immutable
  visibility: public
  semantic_meaning: Training evaluation metrics
  source: derived_from (training)

trained_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Training completion timestamp
  source: system_generated
```

---

### AsyncJob

```yaml
id:
  type: primitive
  data_type: string (UUID)
  nullability: required
  mutability: immutable
  visibility: public
  default_value: auto-generated UUID
  semantic_meaning: Unique job identifier
  source: system_generated

job_type:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  validation_rules: [max_length: 50]
  semantic_meaning: Type of async operation
  source: system_generated

status:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  default_value: "pending"
  validation_rules: [enum: pending|running|completed|failed]
  semantic_meaning: Current job state
  source: system_generated

progress:
  type: primitive
  data_type: integer
  nullability: required
  mutability: mutable
  visibility: public
  default_value: 0
  validation_rules: [0 - 100]
  semantic_meaning: Completion percentage
  source: system_generated

result_json:
  type: composite
  data_type: JSON (object)
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Job result data
  source: system_generated

error:
  type: primitive
  data_type: text
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Error message if failed
  source: system_generated

created_at:
  type: primitive
  data_type: datetime
  nullability: required
  mutability: immutable
  visibility: public
  default_value: current UTC timestamp
  semantic_meaning: Job creation timestamp
  source: system_generated

updated_at:
  type: primitive
  data_type: datetime
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Last status update timestamp
  source: system_generated
```

---

## Frontend Transformed Types

### User (AuthContext)

```yaml
id:
  type: primitive
  data_type: string
  nullability: required
  mutability: immutable
  visibility: public
  semantic_meaning: User identifier
  source: system_generated | external_api

name:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  semantic_meaning: Display name
  source: user_input | derived_from (email)

email:
  type: primitive
  data_type: string
  nullability: required
  mutability: mutable
  visibility: public
  semantic_meaning: User email address
  source: user_input

avatar:
  type: primitive
  data_type: string (URL)
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Profile image URL
  source: user_input

role:
  type: reference
  data_type: enum (admin | user | viewer)
  nullability: optional
  mutability: mutable
  visibility: public
  semantic_meaning: Authorization level
  source: system_generated | external_api
```

---

## Statistics

| Category               | Count |
| ---------------------- | ----- |
| Total ORM Attributes   | ~85   |
| Required Attributes    | ~45   |
| Optional Attributes    | ~40   |
| Computed/Derived       | ~15   |
| JSON Composite         | ~12   |
| Binary Fields          | 3     |
| Foreign Key References | 12    |
| Self-References        | 1     |
| Indexed Fields         | 4     |
