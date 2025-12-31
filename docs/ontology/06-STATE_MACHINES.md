# State Machine Specifications — Formal State Transition Tables

> **ATLAS Ontological Analysis**  
> Generated: 2025-12-31  
> System: Process Mining SaaS Platform

---

## Overview

This document specifies the state machines for all entities that have explicit state transitions, distinguishing between system-maintained and user-maintained states.

---

## WorkflowRun State Machine

### State Diagram

```
                        ┌─────────────┐
                        │   PENDING   │
                        │  (initial)  │
                        └──────┬──────┘
                               │
                    ═══════════▼═══════════
                    ║    Job scheduler     ║
                    ║    picks up run      ║
                    ═══════════╪═══════════
                               │
                        ┌──────▼──────┐
                        │   RUNNING   │
                        └──────┬──────┘
                               │
          ┌────────────────────┴────────────────────┐
          │                                         │
══════════▼══════════                   ════════════▼═══════════
║  All steps pass   ║                   ║  Any step fails       ║
═════════╪══════════                   ════════════╪═══════════
          │                                         │
   ┌──────▼──────┐                          ┌──────▼──────┐
   │  COMPLETED  │                          │   FAILED    │
   │  (terminal) │                          │  (terminal) │
   └─────────────┘                          └─────────────┘

Legend:
  ──────► User-triggered transition
  ══════► System-triggered transition
  [State] Current state
```

### State Transition Table

```yaml
workflow_run_states:
  PENDING:
    description: "Run created, waiting for execution"
    entry_conditions:
      - "workflow.run() called"
    valid_transitions:
      - to: RUNNING
        trigger: job_scheduler_pickup
        maintained_by: SYSTEM
        guards: [worker_available]
        side_effects: [set_started_at]

  RUNNING:
    description: "Workflow steps executing"
    entry_conditions:
      - "Job scheduler picks up pending run"
    valid_transitions:
      - to: COMPLETED
        trigger: all_steps_success
        maintained_by: SYSTEM
        guards: [no_errors]
        side_effects: [set_completed_at, store_result_json]
      - to: FAILED
        trigger: step_error
        maintained_by: SYSTEM
        guards: []
        side_effects: [set_completed_at, store_error]

  COMPLETED:
    description: "All steps executed successfully"
    entry_conditions:
      - "Last step returns success"
    valid_transitions: [] # Terminal
    reversibility: never

  FAILED:
    description: "Execution stopped due to error"
    entry_conditions:
      - "Any step throws exception"
    valid_transitions: [] # Terminal
    reversibility: never
```

---

## AsyncJob State Machine

### State Diagram

```
                        ┌─────────────┐
                        │   PENDING   │
                        │  (initial)  │
                        └──────┬──────┘
                               │
                    ═══════════▼═══════════
                    ║   Worker picks up   ║
                    ═══════════╪═══════════
                               │
                        ┌──────▼──────┐
              ╔════════►│   RUNNING   │◄════════╗
              ║         └──────┬──────┘         ║
              ║                │                ║
              ║    ════════════╪════════════    ║
              ║    ║   Progress updates    ║    ║
              ║    ════════════╪════════════    ║
              ║                │                ║
              ╚════════════════╝                ║
                               │                ║
          ┌────────────────────┴────────────────┘
          │                    │
══════════▼═══════════    ═════▼════════════
║  Work completes    ║    ║  Error occurs   ║
═════════╪═══════════    ═════╪═════════════
          │                    │
   ┌──────▼──────┐      ┌──────▼──────┐
   │  COMPLETED  │      │   FAILED    │
   │  (terminal) │      │  (terminal) │
   └─────────────┘      └─────────────┘
```

### State Transition Table

```yaml
async_job_states:
  pending:
    description: "Job queued, not yet started"
    entry_conditions:
      - "Long-running operation requested"
    valid_transitions:
      - to: running
        trigger: worker_assignment
        maintained_by: SYSTEM
        side_effects: [set_updated_at]

  running:
    description: "Job actively executing"
    entry_conditions:
      - "Worker begins processing"
    valid_transitions:
      - to: running
        trigger: progress_update
        maintained_by: SYSTEM
        guards: [progress <= 100]
        side_effects: [increment_progress, set_updated_at]
      - to: completed
        trigger: work_finished
        maintained_by: SYSTEM
        guards: [no_errors]
        side_effects: [set_progress_100, store_result, set_updated_at]
      - to: failed
        trigger: exception_raised
        maintained_by: SYSTEM
        side_effects: [store_error, set_updated_at]

  completed:
    description: "Job finished successfully"
    entry_conditions:
      - "All work finished without error"
    valid_transitions: [] # Terminal
    data_available: result_json

  failed:
    description: "Job stopped due to error"
    entry_conditions:
      - "Exception during execution"
    valid_transitions: [] # Terminal
    data_available: error
```

---

## Workflow Active State Machine

### State Diagram

```
                        ┌─────────────┐
                        │   ACTIVE    │
                        │is_active=T  │
                        └──────┬──────┘
                               │
              ─────────────────┼─────────────────
              │ User toggles  │                 │
              ▼               │                 ▼
      ┌───────────────┐      │         ┌───────────────┐
      │  DEACTIVATED  │      │         │    DELETED    │
      │ is_active=F   │◄─────┘         │   (terminal)  │
      └───────┬───────┘                └───────────────┘
              │
              │ User toggles
              ▼
      ┌───────────────┐
      │    ACTIVE     │
      │ is_active=T   │
      └───────────────┘
```

### State Transition Table

```yaml
workflow_active_states:
  active:
    description: "Workflow can be executed and scheduled"
    entry_conditions:
      - "New workflow created"
      - "Deactivated workflow reactivated"
    valid_transitions:
      - to: deactivated
        trigger: user_toggle_off
        maintained_by: USER
        required_inputs: []
        side_effects: [cancel_scheduled_runs]
        reversibility: yes
      - to: deleted
        trigger: user_delete
        maintained_by: USER
        required_inputs: [confirmation]
        side_effects: [cascade_delete_runs]
        reversibility: no

  deactivated:
    description: "Workflow exists but won't run"
    entry_conditions:
      - "User sets is_active=false"
    valid_transitions:
      - to: active
        trigger: user_toggle_on
        maintained_by: USER
        required_inputs: []
        side_effects: [resume_schedule]
        reversibility: yes
      - to: deleted
        trigger: user_delete
        maintained_by: USER
        required_inputs: [confirmation]
        side_effects: [cascade_delete_runs]
        reversibility: no

  deleted:
    description: "Workflow removed from system"
    entry_conditions:
      - "User confirms deletion"
    valid_transitions: [] # Terminal
```

---

## EventLog Processing State Machine

> Note: This is an implicit state machine — not stored in a status field but represented by the presence/absence of data and timestamps.

### State Diagram

```
                             ┌─────────────┐
                             │   (none)    │
                             │  No log yet │
                             └──────┬──────┘
                                    │
                    ────────────────▼────────────────
                    │     User uploads file         │
                    ─────────────────────────────────
                                    │
                             ┌──────▼──────┐
                             │  DETECTING  │
                             │  columns    │
                             └──────┬──────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
     Detection fails         User confirms           User cancels
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │    ERROR      │       │   INGESTING   │       │   CANCELLED   │
    │ (return error)│       │               │       │ (no log saved)│
    └───────────────┘       └───────┬───────┘       └───────────────┘
                                    │
                    ════════════════╪════════════════
                    ║  Parse file, create records   ║
                    ════════════════╪════════════════
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
            ════════▼═══════                 ════════▼════════
            ║  Success     ║                 ║  Parse error  ║
            ════════╪══════                  ════════╪════════
                    │                                │
             ┌──────▼──────┐                  ┌──────▼──────┐
             │   ACTIVE    │                  │   FAILED    │
             │ (created_at)│                  │ (exception) │
             └─────────────┘                  └─────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────────┐
    │                   ACTIVE OPERATIONS                    │
    │  - Discovery → creates ProcessModel                   │
    │  - Analytics → creates cache entries                  │
    │  - Filtering → creates NEW EventLog (child)           │
    │  - Predictions → creates PredictionModel              │
    │  - Organizational → creates SocialNetwork             │
    └───────────────────────────────────────────────────────┘
                    │
         ──────────▼──────────
         │  User deletes     │
         ─────────────────────
                    │
             ┌──────▼──────┐
             │   DELETED   │
             │  (terminal) │
             └─────────────┘
```

### Implicit State Detection

```yaml
eventlog_implicit_states:
  none:
    detection: "No EventLog record exists"

  detecting:
    detection: "detect_columns() in progress"
    ephemeral: true # Not persisted

  ingesting:
    detection: "ingest_file() in progress"
    ephemeral: true # Not persisted

  active:
    detection: "EventLog record exists with created_at"
    indicators:
      - id is set
      - created_at is set
      - total_events > 0

  filtered:
    detection: "EventLog with is_filtered=true"
    indicators:
      - is_filtered = true
      - source_log_id is set
      - filter_config_json is not null

  deleted:
    detection: "No longer in database"
```

---

## User Authentication State Machine (Frontend)

### State Diagram

```
                        ┌─────────────┐
                        │ UNAUTHENTICATED │
                        │   (initial)     │
                        └──────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
    ──────▼──────        ──────▼──────        ──────▼──────
    │   Login   │        │ Guest Mode │        │ Token    │
    │  (email/  │        │            │        │ Restore  │
    │  password)│        │            │        │          │
    ─────────────        ─────────────        ─────────────
          │                    │                    │
          │                    │                    │
          │                    │     ═══════════════╧══════════════
          │                    │     ║ Token validation (startup) ║
          │                    │     ═══════════════════════════════
          │                    │                    │
          └────────────────────┴────────────────────┘
                               │
                        ┌──────▼──────┐
                        │ AUTHENTICATED │
                        │   user set    │
                        │ token stored  │
                        └──────┬────────┘
                               │
                    ──────────▼──────────
                    │      Logout       │
                    ─────────────────────
                               │
                        ┌──────▼──────────┐
                        │ UNAUTHENTICATED │
                        │  localStorage   │
                        │   cleared       │
                        └─────────────────┘
```

### State Transition Table

```yaml
auth_states:
  unauthenticated:
    description: "No valid session"
    entry_conditions:
      - "App startup with no stored token"
      - "Logout action"
      - "Token validation failed"
    valid_transitions:
      - to: authenticated
        trigger: login_success
        maintained_by: USER
        required_inputs: [email, password]
        side_effects: [store_token, store_user]
      - to: authenticated
        trigger: guest_login
        maintained_by: USER
        required_inputs: []
        side_effects: [store_guest_token]
      - to: authenticated
        trigger: token_restore
        maintained_by: SYSTEM
        guards: [valid_stored_token]
        side_effects: []

  authenticated:
    description: "Valid session exists"
    entry_conditions:
      - "Successful login"
      - "Valid token restored"
    valid_transitions:
      - to: unauthenticated
        trigger: logout
        maintained_by: USER
        required_inputs: []
        side_effects: [clear_storage, call_logout_api]
      - to: unauthenticated
        trigger: session_expired
        maintained_by: SYSTEM
        guards: [api_returns_401]
        side_effects: [clear_storage]

user_roles:
  admin:
    description: "Full system access"
  user:
    description: "Standard access"
  viewer:
    description: "Read-only access (guest mode)"
```

---

## Conformance Status (Derived State)

> Note: This is not stored but derived from fitness score.

```yaml
conformance_states:
  conformant:
    description: "Model adequately represents log behavior"
    detection: "fitness >= 0.8"
    is_conformant: true

  non_conformant:
    description: "Significant deviations detected"
    detection: "fitness < 0.8"
    is_conformant: false
# Computed in ConformanceResponse schema:
# is_conformant = fitness >= 0.8
```

---

## State Machine Summary

| Entity          | State Field | States                                          | System-Controlled | User-Controlled |
| --------------- | ----------- | ----------------------------------------------- | ----------------- | --------------- |
| **WorkflowRun** | `status`    | pending, running, completed, failed             | 4/4               | 0/4             |
| **AsyncJob**    | `status`    | pending, running, completed, failed             | 4/4               | 0/4             |
| **Workflow**    | `is_active` | active, deactivated, deleted                    | 0/3               | 3/3             |
| **EventLog**    | (implicit)  | detecting, ingesting, active, filtered, deleted | 3/5               | 2/5             |
| **User**        | (context)   | unauthenticated, authenticated                  | 2/2               | 2/2             |
| **Conformance** | (derived)   | conformant, non_conformant                      | 2/2               | 0/2             |

---

## State Persistence

| State Machine | Storage Location       | Transition Logging |
| ------------- | ---------------------- | ------------------ |
| WorkflowRun   | `workflow_runs.status` | updated_at changes |
| AsyncJob      | `async_jobs.status`    | updated_at changes |
| Workflow      | `workflows.is_active`  | updated_at changes |
| EventLog      | Implicit (existence)   | created_at only    |
| User          | `localStorage`         | No server-side log |
| Conformance   | Derived (not stored)   | N/A                |

---

## Transition Guards Summary

| Transition                            | Guards                            |
| ------------------------------------- | --------------------------------- |
| WorkflowRun: pending → running        | worker_available                  |
| WorkflowRun: running → completed      | no_errors, all_steps_success      |
| AsyncJob: running → running           | progress <= 100                   |
| Auth: restore → authenticated         | valid_stored_token                |
| Auth: authenticated → unauthenticated | api_returns_401 (for auto-logout) |
