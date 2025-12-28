# Extracted ERD for Process Mining Platform

Based on your current implementation and the comprehensive ERD provided, here is a **focused extraction** of entities relevant for your next development phases.

## TL;DR - Current State (v0.4.0)

| Layer           | Tables                                                                             | Status    |
| --------------- | ---------------------------------------------------------------------------------- | --------- |
| **Core**        | `event_logs`, `process_cases`, `process_events`, `variants`, `activity_types`      | ✅ Done   |
| **Discovery**   | `process_models`, `model_versions`, `discovery_runs`, `petri_net_*`, `dfg_edges`   | ✅ Done   |
| **Conformance** | `reference_models`, `conformance_runs`, `alignments`, `deviations`, `compliance_*` | ✅ Done   |
| **Performance** | `analysis_runs`, `*_metrics`, `bottlenecks`, `kpis`, `alerts`                      | ✅ Done   |
| **Dashboards**  | `dashboards`, `widgets`, `reports`                                                 | 🔮 Future |

**Total: 41 tables implemented**

---

## Implementation History

| Version  | What Changed                            |
| -------- | --------------------------------------- |
| **v0.1** | Core domain entities                    |
| **v0.2** | Value objects, state machines           |
| **v0.3** | Transitions, resources, SLAs            |
| **v0.4** | Full ERD (25 new models for phases 2-4) |

---

## Phase 1: Core Process Mining (Recommended Next)

These entities extend your existing foundation with versioning, variants, and activities:

```mermaid
erDiagram
    EventLogDataset ||--o{ EventLogVersion : "versions"
    EventLogDataset ||--o{ EventLogStatistics : "summarizes"

    EventLogVersion ||--o{ ProcessCase : "contains"
    EventLogVersion ||--o{ ActivityType : "defines"
    EventLogVersion ||--o{ ResourceEntity : "involves"

    ProcessCase ||--o{ ProcessEvent : "comprises"
    ProcessCase }o--o| ProcessVariant : "classifies"

    ProcessEvent }o--|| ActivityType : "executes"
    ProcessEvent }o--o| ResourceEntity : "performed_by"

    ProcessVariant ||--o{ VariantActivity : "sequences"

    EventLogDataset {
        uuid dataset_id PK
        uuid workspace_id FK
        string dataset_name
        string dataset_slug UK
        text dataset_description
        enum dataset_type "STANDARD|OBJECT_CENTRIC"
        enum dataset_status "IMPORTING|READY|PROCESSING|ERROR|ARCHIVED"
        uuid current_version_id FK
        timestamp dataset_created_at
        uuid created_by_user_id FK
    }

    EventLogVersion {
        uuid version_id PK
        uuid dataset_id FK
        integer version_number
        string version_label
        text version_notes
        enum version_status "DRAFT|ACTIVE|SUPERSEDED|ARCHIVED"
        timestamp observation_start_date
        timestamp observation_end_date
        timestamp version_created_at
        uuid created_by_user_id FK
    }

    EventLogStatistics {
        uuid stats_id PK
        uuid version_id FK
        bigint total_events
        bigint total_cases
        integer distinct_activities
        integer distinct_resources
        interval min_case_duration
        interval max_case_duration
        interval avg_case_duration
        interval median_case_duration
        decimal avg_events_per_case
        timestamp stats_computed_at
    }

    ActivityType {
        uuid activity_type_id PK
        uuid version_id FK
        string activity_name UK
        string activity_code
        string activity_category
        enum activity_type "TASK|DECISION|START|END|INTERMEDIATE|SUBPROCESS"
        boolean is_automated
        boolean is_value_adding
        bigint occurrence_count
        interval avg_processing_time
        decimal avg_cost
    }

    ResourceEntity {
        uuid resource_id PK
        uuid version_id FK
        string resource_identifier UK
        string resource_name
        enum resource_type "HUMAN|SYSTEM|BOT|EXTERNAL"
        string resource_role
        string resource_department
        decimal resource_hourly_cost
        bigint total_events_performed
        integer distinct_activities_performed
    }

    ProcessVariant {
        uuid variant_id PK
        uuid event_log_version_id FK
        string variant_hash UK
        text variant_activity_trace
        integer variant_length
        bigint variant_case_count
        decimal variant_frequency_percent
        interval variant_avg_duration
        boolean is_happy_path
        boolean is_compliant
        integer variant_rank
    }

    VariantActivity {
        uuid variant_activity_id PK
        uuid variant_id FK
        uuid activity_type_id FK
        integer sequence_position
    }
```

---

## Phase 2: Process Discovery & Model Management

Extends your existing `ProcessModel` with versioning, Petri net, and BPMN support:

```mermaid
erDiagram
    ProcessModelRepository ||--o{ ProcessModel : "catalogs"
    ProcessModel ||--o{ ProcessModelVersion : "versions"

    ProcessDiscoveryRun ||--|| ProcessModelVersion : "produces"
    ProcessDiscoveryRun }o--|| EventLogVersion : "mines_from"

    ProcessModelVersion ||--o{ PetriNetPlace : "defines"
    ProcessModelVersion ||--o{ PetriNetTransition : "defines"
    ProcessModelVersion ||--o{ PetriNetArc : "connects"
    ProcessModelVersion ||--o{ DirectlyFollowsEdge : "links"
    ProcessModelVersion ||--o{ ModelQualityMetric : "measured_by"

    ProcessModelRepository {
        uuid repository_id PK
        uuid workspace_id FK
        string repository_name
        text repository_description
        enum repository_type "DISCOVERED|REFERENCE|IMPORTED"
        timestamp repository_created_at
    }

    ProcessModel {
        uuid model_id PK
        uuid repository_id FK
        string model_name
        string model_slug UK
        text model_description
        enum model_source "DISCOVERED|IMPORTED|MANUAL|REFERENCE"
        enum model_status "DRAFT|UNDER_REVIEW|APPROVED|PUBLISHED|DEPRECATED"
        uuid current_version_id FK
        uuid source_event_log_id FK
        timestamp model_created_at
        uuid created_by_user_id FK
    }

    ProcessDiscoveryRun {
        uuid discovery_run_id PK
        uuid workspace_id FK
        uuid event_log_version_id FK
        uuid initiated_by_user_id FK
        enum discovery_algorithm "ALPHA|ALPHA_PLUS|HEURISTIC|INDUCTIVE|INDUCTIVE_INFREQUENT|DFG"
        enum output_notation "PETRI_NET|BPMN|PROCESS_TREE|DFG"
        enum run_status "QUEUED|PREPROCESSING|MINING|EVALUATING|COMPLETED|FAILED"
        integer progress_percentage
        timestamp run_started_at
        timestamp run_completed_at
        text error_message
        bigint events_processed
    }

    ProcessModelVersion {
        uuid version_id PK
        uuid model_id FK
        uuid discovery_run_id FK
        integer version_number
        string version_label
        enum version_status "DRAFT|ACTIVE|ARCHIVED"
        enum notation_type "PETRI_NET|BPMN|PROCESS_TREE|DFG"
        jsonb model_serialized_json
        text model_pnml
        text model_bpmn_xml
        bytea model_image_svg
        jsonb canvas_layout
        timestamp version_created_at
    }

    ModelQualityMetric {
        uuid metric_id PK
        uuid version_id FK
        uuid evaluated_against_log_id FK
        enum metric_type "FITNESS|PRECISION|GENERALIZATION|SIMPLICITY|SOUNDNESS"
        decimal metric_value
        jsonb metric_details
        timestamp metric_computed_at
    }

    PetriNetPlace {
        uuid place_id PK
        uuid version_id FK
        string place_id_internal
        string place_name
        integer initial_tokens
        boolean is_initial_place
        boolean is_final_place
        decimal position_x
        decimal position_y
    }

    PetriNetTransition {
        uuid transition_id PK
        uuid version_id FK
        uuid mapped_activity_id FK
        string transition_id_internal
        string transition_name
        boolean is_silent
        interval avg_duration
        bigint firing_frequency
        decimal position_x
        decimal position_y
    }

    PetriNetArc {
        uuid arc_id PK
        uuid version_id FK
        uuid from_place_id FK
        uuid from_transition_id FK
        uuid to_place_id FK
        uuid to_transition_id FK
        enum arc_type "NORMAL|INHIBITOR|RESET|READ"
        integer arc_weight
    }

    DirectlyFollowsEdge {
        uuid edge_id PK
        uuid version_id FK
        uuid source_activity_id FK
        uuid target_activity_id FK
        bigint edge_frequency
        decimal edge_probability
        interval avg_transition_time
        interval median_transition_time
    }
```

---

## Phase 3: Conformance & Compliance

Extends your existing `ConformanceResult` with detailed deviations and compliance rules:

```mermaid
erDiagram
    ReferenceModel ||--o{ ConformanceCheckRun : "validated_against"
    ReferenceModel ||--o{ ComplianceRule : "enforces"
    ReferenceModel }o--|| ProcessModelVersion : "based_on"

    ConformanceCheckRun ||--o{ CaseConformanceResult : "evaluates"
    ConformanceCheckRun ||--o{ DeviationType : "identifies"
    ConformanceCheckRun }o--|| EventLogVersion : "checks"

    CaseConformanceResult ||--o{ AlignmentStep : "aligned_via"
    CaseConformanceResult ||--o{ DeviationInstance : "exhibits"

    DeviationType ||--o{ DeviationInstance : "manifests_as"
    ComplianceRule ||--o{ ComplianceViolation : "violated_in"

    ReferenceModel {
        uuid reference_model_id PK
        uuid workspace_id FK
        uuid process_model_version_id FK
        string reference_name
        text reference_description
        enum reference_source "DISCOVERED|IMPORTED|DESIGNED|REGULATORY"
        enum reference_status "DRAFT|ACTIVE|DEPRECATED"
        boolean is_normative
        string regulatory_framework
        timestamp effective_from
        uuid created_by_user_id FK
    }

    ConformanceCheckRun {
        uuid check_run_id PK
        uuid workspace_id FK
        uuid event_log_version_id FK
        uuid reference_model_id FK
        uuid initiated_by_user_id FK
        enum check_algorithm "TOKEN_REPLAY|ALIGNMENT_BASED|FOOTPRINT|BEHAVIORAL_PROFILE"
        enum run_status "QUEUED|REPLAYING|ALIGNING|ANALYZING|COMPLETED|FAILED"
        integer progress_percentage
        timestamp run_started_at
        timestamp run_completed_at
        decimal overall_fitness_score
        decimal overall_precision_score
        bigint total_cases_checked
        bigint fitting_cases_count
        bigint non_fitting_cases_count
    }

    CaseConformanceResult {
        uuid case_result_id PK
        uuid check_run_id FK
        uuid case_id FK
        boolean is_fitting
        decimal case_fitness_score
        integer alignment_cost
        integer synchronous_moves
        integer model_moves
        integer log_moves
        integer deviation_count
    }

    AlignmentStep {
        uuid step_id PK
        uuid case_result_id FK
        integer step_index
        enum step_type "SYNC|MODEL_MOVE|LOG_MOVE|INVISIBLE"
        string log_activity_name
        string model_activity_name
        uuid log_event_id FK
        integer step_cost
    }

    DeviationType {
        uuid deviation_type_id PK
        uuid check_run_id FK
        uuid activity_type_id FK
        enum deviation_category "MISSING_ACTIVITY|UNEXPECTED_ACTIVITY|WRONG_SEQUENCE|SKIPPED_MANDATORY|REPEATED_ACTIVITY|TIMING_VIOLATION"
        string deviation_name
        enum deviation_severity "LOW|MEDIUM|HIGH|CRITICAL"
        bigint occurrence_count
        decimal occurrence_rate
    }

    DeviationInstance {
        uuid instance_id PK
        uuid deviation_type_id FK
        uuid case_id FK
        uuid event_id FK
        timestamp deviation_detected_at
        text instance_details
    }

    ComplianceRule {
        uuid rule_id PK
        uuid reference_model_id FK
        string rule_name
        string rule_code UK
        text rule_description
        enum rule_type "EXISTENCE|ABSENCE|EXACTLY|RESPONSE|PRECEDENCE|SUCCESSION|CHAIN_RESPONSE"
        text rule_ltl_expression
        enum rule_severity "INFO|WARNING|ERROR|CRITICAL"
        boolean is_mandatory
        boolean is_enabled
    }

    ComplianceViolation {
        uuid violation_id PK
        uuid check_run_id FK
        uuid rule_id FK
        uuid case_id FK
        uuid event_id FK
        text violation_description
        jsonb violation_evidence
        timestamp violation_detected_at
    }
```

---

## Phase 4: Performance Analytics & KPIs

Extends your existing SLA models with bottleneck detection and KPIs:

```mermaid
erDiagram
    PerformanceAnalysisRun ||--o{ ActivityPerformanceMetric : "measures"
    PerformanceAnalysisRun ||--o{ TransitionPerformanceMetric : "measures"
    PerformanceAnalysisRun ||--o{ ResourcePerformanceMetric : "measures"
    PerformanceAnalysisRun ||--o{ BottleneckFinding : "identifies"
    PerformanceAnalysisRun }o--|| EventLogVersion : "analyzes"

    ProcessKPI ||--o{ KPIMeasurement : "tracked_by"
    ProcessKPI ||--o{ KPITarget : "targets"
    ProcessKPI ||--o{ KPIAlert : "triggers"

    PerformanceAnalysisRun {
        uuid analysis_run_id PK
        uuid workspace_id FK
        uuid event_log_version_id FK
        uuid initiated_by_user_id FK
        string analysis_name
        enum analysis_type "DURATION|FREQUENCY|BOTTLENECK|THROUGHPUT|WORKLOAD"
        enum run_status "QUEUED|PROCESSING|COMPLETED|FAILED"
        timestamp run_started_at
        timestamp run_completed_at
        jsonb summary_statistics
    }

    ActivityPerformanceMetric {
        uuid metric_id PK
        uuid analysis_run_id FK
        uuid activity_type_id FK
        bigint execution_count
        bigint distinct_cases
        interval min_duration
        interval max_duration
        interval avg_duration
        interval median_duration
        interval p95_duration
        interval total_processing_time
        interval total_waiting_time
        decimal avg_cost
    }

    TransitionPerformanceMetric {
        uuid metric_id PK
        uuid analysis_run_id FK
        uuid from_activity_id FK
        uuid to_activity_id FK
        bigint transition_count
        interval min_time
        interval max_time
        interval avg_time
        interval median_time
        decimal transition_probability
    }

    ResourcePerformanceMetric {
        uuid metric_id PK
        uuid analysis_run_id FK
        uuid resource_id FK
        bigint events_handled
        bigint cases_touched
        integer distinct_activities
        interval total_active_time
        interval avg_handling_time
        decimal utilization_rate
        bigint handoff_count_out
        bigint handoff_count_in
    }

    BottleneckFinding {
        uuid finding_id PK
        uuid analysis_run_id FK
        uuid activity_type_id FK
        uuid from_activity_id FK
        uuid to_activity_id FK
        enum bottleneck_location "ACTIVITY|TRANSITION|RESOURCE|BATCH_POINT"
        enum bottleneck_type "PROCESSING_TIME|WAITING_TIME|RESOURCE_CONTENTION|BATCHING"
        decimal severity_score
        interval avg_delay_introduced
        interval total_time_impact
        bigint cases_affected
        text bottleneck_description
        text recommended_action
    }

    ProcessKPI {
        uuid kpi_id PK
        uuid workspace_id FK
        string kpi_name
        string kpi_code UK
        text kpi_description
        enum kpi_category "TIME|COST|QUALITY|THROUGHPUT|COMPLIANCE|CUSTOM"
        text kpi_formula
        string kpi_unit
        enum kpi_direction "HIGHER_IS_BETTER|LOWER_IS_BETTER"
        boolean is_enabled
        uuid created_by_user_id FK
    }

    KPIMeasurement {
        uuid measurement_id PK
        uuid kpi_id FK
        uuid event_log_version_id FK
        timestamp measurement_period_start
        timestamp measurement_period_end
        decimal measurement_value
        decimal previous_period_value
        decimal change_percent
        bigint sample_size
        timestamp measured_at
    }

    KPITarget {
        uuid target_id PK
        uuid kpi_id FK
        string target_name
        decimal target_value
        enum target_type "MINIMUM|MAXIMUM|EXACT|RANGE"
        decimal target_range_low
        decimal target_range_high
        timestamp target_effective_from
        uuid set_by_user_id FK
    }

    KPIAlert {
        uuid kpi_alert_id PK
        uuid kpi_id FK
        uuid target_id FK
        uuid measurement_id FK
        enum alert_type "TARGET_BREACH|TREND_DECLINE|ANOMALY"
        decimal actual_value
        decimal target_value
        decimal deviation_percent
        text alert_message
        timestamp alert_triggered_at
        boolean is_acknowledged
    }
```

---

## Phase 5: Dashboards & Reporting (Future)

```mermaid
erDiagram
    Dashboard ||--o{ DashboardVersion : "versions"
    Dashboard ||--o{ DashboardShare : "shared_via"
    DashboardVersion ||--o{ DashboardWidget : "contains"
    DashboardWidget ||--o{ WidgetDataBinding : "binds"

    ReportTemplate ||--o{ ReportGeneration : "generates"
    ReportTemplate ||--o{ ReportSchedule : "scheduled_by"

    ExportJob ||--o{ ExportFile : "produces"

    Dashboard {
        uuid dashboard_id PK
        uuid workspace_id FK
        string dashboard_name
        string dashboard_slug UK
        text dashboard_description
        enum dashboard_type "OVERVIEW|PERFORMANCE|CONFORMANCE|CUSTOM"
        enum dashboard_status "DRAFT|PUBLISHED|ARCHIVED"
        boolean is_default
        uuid current_version_id FK
        uuid created_by_user_id FK
        timestamp dashboard_created_at
    }

    DashboardVersion {
        uuid version_id PK
        uuid dashboard_id FK
        integer version_number
        jsonb layout_config
        jsonb global_filters
        timestamp version_created_at
        uuid created_by_user_id FK
    }

    DashboardWidget {
        uuid widget_id PK
        uuid version_id FK
        string widget_title
        enum widget_type "PROCESS_MAP|VARIANT_CHART|KPI_CARD|TIME_SERIES|BAR_CHART|PIE_CHART|TABLE|FUNNEL|HEATMAP|SANKEY"
        jsonb widget_config
        integer grid_x
        integer grid_y
        integer grid_width
        integer grid_height
        integer widget_order
    }

    WidgetDataBinding {
        uuid binding_id PK
        uuid widget_id FK
        uuid event_log_version_id FK
        uuid process_model_version_id FK
        uuid analysis_run_id FK
        uuid kpi_id FK
        jsonb data_query
        jsonb data_transformations
    }

    DashboardShare {
        uuid share_id PK
        uuid dashboard_id FK
        uuid shared_by_user_id FK
        uuid shared_with_user_id FK
        string public_share_token UK
        enum share_permission "VIEW|INTERACT|EDIT"
        timestamp share_created_at
        boolean is_public
    }

    ReportTemplate {
        uuid template_id PK
        uuid workspace_id FK
        string template_name
        text template_description
        enum report_format "PDF|EXCEL|POWERPOINT|HTML"
        jsonb template_sections
        jsonb template_styles
        uuid created_by_user_id FK
        timestamp template_created_at
    }

    ReportGeneration {
        uuid generation_id PK
        uuid template_id FK
        uuid event_log_version_id FK
        uuid initiated_by_user_id FK
        jsonb report_parameters
        enum generation_status "QUEUED|GENERATING|COMPLETED|FAILED"
        timestamp generation_started_at
        timestamp generation_completed_at
        string output_file_path
    }

    ReportSchedule {
        uuid schedule_id PK
        uuid template_id FK
        string schedule_name
        string cron_expression
        string schedule_timezone
        jsonb recipient_emails
        boolean is_enabled
        timestamp next_run_at
        timestamp last_run_at
    }

    ExportJob {
        uuid export_job_id PK
        uuid workspace_id FK
        uuid initiated_by_user_id FK
        enum export_type "EVENT_LOG|PROCESS_MODEL|ANALYSIS_RESULTS|DASHBOARD_SNAPSHOT"
        uuid source_id
        enum export_format "XES|CSV|PARQUET|PNML|BPMN|JSON|PNG|SVG"
        enum job_status "QUEUED|EXPORTING|COMPLETED|FAILED|EXPIRED"
        timestamp job_started_at
        timestamp job_completed_at
    }

    ExportFile {
        uuid file_id PK
        uuid export_job_id FK
        string file_name
        string file_path
        string file_mime_type
        bigint file_size_bytes
        string file_checksum_sha256
        timestamp file_created_at
    }
```

---

## Recommended Implementation Order

| Phase | Entities                                                                  | Priority   | Extends                         |
| ----- | ------------------------------------------------------------------------- | ---------- | ------------------------------- |
| **1** | EventLogVersion, ActivityType, ResourceEntity, ProcessVariant             | **HIGH**   | Your existing EventLog          |
| **2** | ProcessModelVersion, PetriNet\*, DirectlyFollowsEdge, ModelQualityMetric  | **HIGH**   | Your existing ProcessModel      |
| **3** | ConformanceCheckRun, CaseConformanceResult, DeviationType, ComplianceRule | **MEDIUM** | Your existing ConformanceResult |
| **4** | PerformanceAnalysisRun, BottleneckFinding, ProcessKPI, KPIMeasurement     | **MEDIUM** | Your existing SLA models        |
| **5** | Dashboard, Widget, ReportTemplate                                         | **FUTURE** | New capability                  |

---

## Skipped Sections (Lower Priority for MVP)

The following sections from the full ERD are **NOT recommended** for your next phases:

- **Section 1**: Tenant, Workspace, User, Role, Permission (Multi-tenancy) — Only needed at scale
- **Section 6**: Social Network Analysis, Role Mining — Advanced organizational features
- **Section 7**: Predictive Models, Anomaly Detection — ML/AI features
- **Section 9**: Automation Workflows, Triggers — Workflow automation
- **Section 10**: Alerting, Notifications — Production monitoring
- **Section 11**: Integration Providers, OAuth — Third-party connections
- **Section 12**: Audit, GDPR, Data Retention — Compliance (enterprise)

These can be added later when your core process mining functionality is mature.
