DAG Migration Architecture Plan
Migrate the Process Mining backend from simple Celery tasks with independent job tracking to a DAG-based workflow orchestration system.

1. Current State Analysis
1.1 async_jobs Table Schema
Column	Type	Purpose
id
varchar(36)	Primary key (UUID)
task_id
varchar(255)	Celery task ID (unique)
user_id	varchar(36)	User who initiated the job
job_type	varchar(50)	Type of job (ingestion, discovery, etc.)
status	varchar(20)	Job lifecycle state
progress
int	Progress percentage (0-100)
stage	varchar(100)	Current execution stage
entity_type	varchar(50)	Type of entity created/affected
entity_id	varchar(36)	ID of related entity
parent_job_id	varchar(36)	Parent job for chained jobs
parameters_json	text	Input parameters
result_json	text	Output results
error / error_message	text	Error details
created_at / started_at / completed_at	datetime	Timestamps
1.2 Background Task Triggering
Tasks are triggered via Celery's .delay() method from API routers:

Task	Trigger Location	Pattern
validate_uploaded_file_task
upload.py
Direct .delay() call
ingest_dataset_task
ingestion.py
JobService.create() → .delay()
perform_discovery_task
discovery/router.py
Direct .delay() call
perform_analysis_task
analyses/router.py
Direct .delay() call
perform_conformance_task
conformance/router.py
Direct .delay() call
train_prediction_model_task
predictions/router.py
Direct .delay() call
1.3 Current Task Types
From 
enums.py
:

JobType	Description
INGESTION	Dataset parsing and ingestion
VALIDATION	File validation and column detection
DISCOVERY	Process model discovery
CONFORMANCE	Conformance checking
PREDICTION_TRAINING	ML model training
OCEL_IMPORT	OCEL file import
SIMULATION	Process simulation
FILTERING	Dataset filtering
FLATTEN	OCEL flattening
ANALYSIS	General analysis (bottleneck, etc.)
1.4 Existing Workflow System
Located in 
models/workflow.py
:

Current Design: Simple step-based JSON workflows (steps_json field)
Limitations:
No true dependency graph – steps are sequential only
No parallel execution support
No built-in retry at step level
No conditional branching
2. DAG Architecture Design
2.1 Nodes (Tasks) and Edges (Dependencies)
ML Pipeline
Analysis Pipeline
Dataset Pipeline
Upload File
Validate File
Detect Columns
Map Columns
Ingest Dataset
Discover Model
Compute Statistics
Conformance Check
Generate Visualization
Generate Report
Train Predictor
Evaluate Model
Node Definition:

Field	Type	Description
id
UUID	Unique step identifier
dag_run_id	UUID	Parent DAG execution
task_name	string	Reusable task function name
parameters_json	JSON	Task input parameters
status	enum	pending/running/completed/failed/skipped
result_json	JSON	Task output
retry_count	int	Retry attempts made
started_at / completed_at	datetime	Timing
Edge Definition:

Field	Type	Description
id
UUID	Unique edge identifier
dag_definition_id	UUID	Parent DAG template
from_step_id	UUID	Source step
to_step_id	UUID	Target step
condition	JSON	Optional conditional expression
2.2 Tool Recommendation
IMPORTANT

Recommendation: Custom SQL-based DAG Engine

Option	Pros	Cons	Fit
Temporal	Battle-tested, workflow versioning	Heavy infra (Go runtime), steep learning curve	❌ Overkill
Prefect	Python-native, good observability	Self-hosted complexity, memory overhead	⚠️ Medium
Airflow	Industry standard, mature	Designed for batch ETL, heavy scheduler	❌ Poor fit
Custom SQL	Fits existing stack, low latency, full control	Dev effort required	✅ Best fit
Rationale:

Your stack already uses Celery + PostgreSQL/SQLite
Process mining workflows are relatively simple DAGs (5-10 nodes)
Custom engine allows tight integration with existing async_jobs table
No new infrastructure dependencies
2.3 Integration with Existing Tables
Existing Tables
New Tables
1:1
N:1
migrates
migrates
dag_definitions
dag_definition_steps
dag_definition_edges
dag_runs
dag_run_steps
async_jobs
workflows
workflow_runs
3. Schema & Code Changes
3.1 Database Schema Changes
[NEW] dag_definitions
CREATE TABLE dag_definitions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version INT NOT NULL DEFAULT 1,
    steps_json TEXT NOT NULL,      -- Legacy: for simple view
    edges_json TEXT NOT NULL,      -- Legacy: for simple view
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME
);
[NEW] dag_definition_steps
CREATE TABLE dag_definition_steps (
    id VARCHAR(36) PRIMARY KEY,
    dag_definition_id VARCHAR(36) NOT NULL REFERENCES dag_definitions(id),
    name VARCHAR(100) NOT NULL,
    task_name VARCHAR(100) NOT NULL,  -- Maps to Celery task
    default_params_json TEXT,
    retry_policy_json TEXT,           -- {"max_retries": 3, "backoff": "exponential"}
    timeout_seconds INT DEFAULT 3600,
    position INT NOT NULL,
    UNIQUE(dag_definition_id, name)
);
[NEW] dag_definition_edges
CREATE TABLE dag_definition_edges (
    id VARCHAR(36) PRIMARY KEY,
    dag_definition_id VARCHAR(36) NOT NULL REFERENCES dag_definitions(id),
    from_step_id VARCHAR(36) NOT NULL REFERENCES dag_definition_steps(id),
    to_step_id VARCHAR(36) NOT NULL REFERENCES dag_definition_steps(id),
    condition_json TEXT,              -- Optional: {"on_status": "completed", "expression": "..."}
    UNIQUE(dag_definition_id, from_step_id, to_step_id)
);
[NEW] dag_runs
CREATE TABLE dag_runs (
    id VARCHAR(36) PRIMARY KEY,
    dag_definition_id VARCHAR(36) NOT NULL REFERENCES dag_definitions(id),
    user_id VARCHAR(36),
    status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed/failed/cancelled
    trigger_type VARCHAR(50),              -- api/scheduled/webhook
    context_json TEXT,                     -- Shared context passed to all steps
    started_at DATETIME,
    completed_at DATETIME,
    created_at DATETIME NOT NULL,
    -- Link to existing job tracking
    root_job_id VARCHAR(36) REFERENCES async_jobs(id)
);
[NEW] dag_run_steps
CREATE TABLE dag_run_steps (
    id VARCHAR(36) PRIMARY KEY,
    dag_run_id VARCHAR(36) NOT NULL REFERENCES dag_runs(id),
    definition_step_id VARCHAR(36) NOT NULL REFERENCES dag_definition_steps(id),
    status VARCHAR(20) DEFAULT 'pending',
    parameters_json TEXT,
    result_json TEXT,
    error_message TEXT,
    retry_count INT DEFAULT 0,
    started_at DATETIME,
    completed_at DATETIME,
    -- Link to Celery task
    celery_task_id VARCHAR(255),
    -- Link to existing job
    job_id VARCHAR(36) REFERENCES async_jobs(id)
);
[MODIFY] async_jobs (add columns)
ALTER TABLE async_jobs ADD COLUMN dag_run_id VARCHAR(36) REFERENCES dag_runs(id);
ALTER TABLE async_jobs ADD COLUMN dag_step_id VARCHAR(36) REFERENCES dag_run_steps(id);
3.2 Code Areas for Refactoring
Current Location	Refactor To	Notes
dataset_tasks.py
src/platform/dag/tasks/dataset.py	Split into reusable functions
analysis_tasks.py
src/platform/dag/tasks/analysis.py	Extract core logic
ml_tasks.py
src/platform/dag/tasks/prediction.py	Keep as standalone task
JobService
src/platform/dag/service.py	Add DAG orchestration methods
WorkflowService
Deprecate	Replace with DAG engine
New Components:

Component	Location	Purpose
DAGEngine	src/platform/dag/engine.py	Core DAG execution logic
DAGScheduler	src/platform/dag/scheduler.py	Determines ready-to-run steps
DAGRepository	src/platform/dag/repository.py	DB operations
DAGService	src/platform/dag/service.py	Business logic
DAGRouter	src/platform/dag/router.py	API endpoints
4. Migration Roadmap
Phase 1: Infrastructure Setup (Week 1-2)
Task	Owner	Status
Create Alembic migration for new DAG tables	Backend	☐
Add dag_run_id and dag_step_id columns to async_jobs	Backend	☐
Implement DAGDefinition, DAGRun, DAGRunStep SQLAlchemy models	Backend	☐
Implement DAGRepository with CRUD operations	Backend	☐
Implement DAGEngine core logic (topological sort, ready check)	Backend	☐
Unit tests for DAG engine	Backend	☐
Deliverables:

New database tables created
DAGEngine can execute simple 3-node DAG in memory
Phase 2: Refactoring Tasks into DAG Nodes (Week 3-4)
Task	Owner	Status
Extract pure functions from 
dataset_tasks.py
Backend	☐
Create TaskRegistry for mapping task names to functions	Backend	☐
Implement validate_file as DAG-compatible task	Backend	☐
Implement 
ingest_dataset
 as DAG-compatible task	Backend	☐
Implement discover_model as DAG-compatible task	Backend	☐
Implement check_conformance as DAG-compatible task	Backend	☐
Create predefined DAG templates (data_ingestion, full_analysis)	Backend	☐
Integration tests for DAG-based ingestion	Backend	☐
Task Function Signature:

@task_registry.register("validate_file")
async def validate_file(
    context: DAGContext,
    params: dict,
) -> dict:
    """
    Args:
        context: Shared DAG context (dataset_id, user_id, etc.)
        params: Step-specific parameters
    Returns:
        dict: Result to pass to downstream tasks
    """
Phase 3: API Updates (Week 5-6)
Task	Owner	Status
Create /api/v1/dags router	Backend	☐
Implement POST /dags/definitions - Create DAG template	Backend	☐
Implement GET /dags/definitions - List templates	Backend	☐
Implement POST /dags/runs - Trigger DAG execution	Backend	☐
Implement GET /dags/runs/{id} - Get run status with step details	Backend	☐
Implement POST /dags/runs/{id}/cancel - Cancel running DAG	Backend	☐
Update /datasets/ingest to trigger DAG instead of single task	Backend	☐
Update /discovery/discover to trigger DAG	Backend	☐
Add SSE endpoint for DAG progress streaming	Backend	☐
Update frontend to consume new DAG endpoints	Frontend	☐
API Examples:

# Trigger a predefined DAG
POST /api/v1/dags/runs
{
  "dag_definition_id": "full_analysis",
  "context": {"dataset_id": "abc-123"},
  "parameters": {
    "discover_model": {"miner_type": "inductive"},
    "check_conformance": {"method": "token_replay"}
  }
}
# Response
{
  "dag_run_id": "run-456",
  "status": "pending",
  "steps": [
    {"name": "discover_model", "status": "pending"},
    {"name": "check_conformance", "status": "pending", "depends_on": ["discover_model"]}
  ]
}
Verification Plan
Automated Tests
Test	Command	Purpose
DAG Engine Unit Tests	pytest tests/unit/dag/ -v	Test topological sort, ready check
DAG Repository Tests	pytest tests/integration/dag/ -v	Test DB operations
DAG API Tests	pytest tests/api/test_dags.py -v	Test endpoints
Existing Task Tests	pytest tests/api/test_e2e_process_mining_flow.py -v	Ensure no regression
Manual Verification
Trigger DAG via API: Use Swagger UI at http://localhost:8000/docs to call POST /api/v1/dags/runs with a predefined template
Monitor Progress: Check GET /api/v1/dags/runs/{id} returns step-by-step status
Verify Job Linkage: Confirm async_jobs records have dag_run_id and dag_step_id populated
Test Failure Handling: Cause a step to fail and verify downstream steps are skipped
User Review Required
IMPORTANT

Decision Required: Orchestration Tool

The plan recommends a custom SQL-based DAG engine. If you prefer using Temporal/Prefect instead, the implementation approach will change significantly. Please confirm:

Custom SQL DAG engine (recommended for your stack)
Temporal (requires Go infrastructure)
Prefect (requires Prefect server)
WARNING

Breaking Changes

The existing POST /api/v1/datasets/{id}/ingest endpoint will change behavior to trigger a DAG instead of a single task
Frontend polling logic may need updates to handle DAG run responses
The workflows and workflow_runs tables will be deprecated in favor of DAG tables