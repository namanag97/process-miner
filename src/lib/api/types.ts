/**
 * Shared API Types
 * 
 * Single source of truth for all API types.
 * Used by both client.ts and React Query hooks.
 */

// =============================================================================
// Core Entity Types
// =============================================================================

export interface ColumnMetadata {
    name: string;
    detected_type: 'string' | 'number' | 'datetime' | 'boolean';
    sample_values: string[];
    null_percentage: number;
    unique_count: number;
    detected_format?: string;
}

export interface UploadResponse {
    upload_id: string;
    filename: string;
    file_size_bytes: number;
    row_count: number;
    columns: ColumnMetadata[];
    created_at: string;
}

export interface MappingCreate {
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    timestamp_format?: string;
    resource_column?: string;
    cost_column?: string;
}

export interface MappingResponse {
    mapping_id: string;
    upload_id: string;
    case_id_column: string;
    activity_column: string;
    timestamp_column: string;
    timestamp_format?: string;
    resource_column?: string;
    cost_column?: string;
    created_at: string;
}

// =============================================================================
// Validation Types
// =============================================================================

export interface ValidationError {
    field: string;
    message: string;
    sample_bad_values?: string[];
}

export interface ValidationWarning {
    field: string;
    message: string;
    suggestion?: string;
}

export interface ValidationStats {
    total_rows: number;
    valid_rows: number;
    case_count: number;
    activity_count: number;
    date_range_start?: string;
    date_range_end?: string;
}

export interface ValidationResult {
    is_valid: boolean;
    errors: ValidationError[];
    warnings: ValidationWarning[];
    stats?: ValidationStats;
}

// =============================================================================
// Job Types
// =============================================================================

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface JobResponse {
    job_id: string;
    status: JobStatus;
    progress: number;
    progress_message?: string;
    dataset_id?: string;
    error?: string;
    created_at: string;
    completed_at?: string;
}

// =============================================================================
// Analysis Types
// =============================================================================

export interface ActivityNodeData {
    label: string;
    frequency: number;
    isStart: boolean;
    isEnd: boolean;
    avgDuration: number;
    maxFrequency: number;
}

export interface DFGNode {
    id: string;
    type: string;
    position: { x: number; y: number };
    data: ActivityNodeData;
}

export interface DFGEdge {
    id: string;
    source: string;
    target: string;
    type: string;
    data: {
        frequency: number;
        avgDuration: number;
    };
}

export interface DFGSummary {
    totalCases: number;
    totalEvents: number;
    totalActivities: number;
    totalVariants: number;
}

export interface DFGResponse {
    nodes: DFGNode[];
    edges: DFGEdge[];
    summary: DFGSummary;
}

export interface VariantItem {
    id: string;
    sequence: string[];
    trace_display: string;
    case_count: number;
    percentage: number;
    avg_duration_ms: number;
    is_happy_path: boolean;
    case_ids: string[];
}

export interface VariantsResponse {
    total: number;
    variants: VariantItem[];
}

export interface ProcessStats {
    total_cases: number;
    total_events: number;
    total_activities: number;
    total_variants: number;
    avg_case_duration_ms: number;
    median_case_duration_ms: number;
    start_activities: string[];
    end_activities: string[];
}

export interface DatasetSummary {
    dataset_id: string;
    stats: ProcessStats;
    created_at: string;
}

export interface Deviation {
    type: 'rework' | 'skip' | 'unusual_path';
    description: string;
    affected_cases: string[];
    frequency: number;
}

export interface FullAnalysisResponse {
    dataset_id: string;
    dfg: DFGResponse;
    variants: VariantsResponse;
    stats: ProcessStats;
    deviations: Deviation[];
    created_at: string;
}

// =============================================================================
// Organization & Process Types
// =============================================================================

export interface Organization {
    id: string;
    name: string;
    slug: string;
    description: string | null;
    created_at: string;
    user_count: number;
    process_count: number;
}

export interface OrganizationCreate {
    name: string;
    description?: string;
}

export interface Process {
    id: string;
    org_id: string;
    name: string;
    description: string | null;
    status: 'active' | 'archived' | 'draft';
    icon: string | null;
    color: string | null;
    created_at: string;
    updated_at: string;
    upload_count: number;
    dataset_count: number;
}

export interface ProcessCreate {
    name: string;
    description?: string;
    icon?: string;
    color?: string;
}

export interface ProcessUpdate {
    name?: string;
    description?: string;
    status?: string;
    icon?: string;
    color?: string;
}

// =============================================================================
// Insight Types
// =============================================================================

export type InsightType = 'bottleneck' | 'rework' | 'deviation' | 'kpi_alert' | 'recommendation';
export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';

export interface Insight {
    id: string;
    dataset_id: string;
    insight_type: InsightType;
    severity: SeverityLevel;
    severity_score: number;
    title: string;
    description: string;
    affected_activity: string | null;
    affected_case_count: number;
    metric_name: string | null;
    metric_value: number | null;
    is_acknowledged: boolean;
    created_at: string;
}

export interface InsightSummary {
    total_insights: number;
    by_type: Record<string, number>;
    by_severity: Record<string, number>;
    critical_count: number;
    unacknowledged_count: number;
}

// =============================================================================
// Audit Log Types
// =============================================================================

export type AuditAction = 'create' | 'update' | 'delete' | 'view' | 'process' | 'export' | 'login';

export interface AuditLog {
    id: string;
    user_id: string | null;
    entity_type: string;
    entity_id: string | null;
    action: AuditAction;
    details: Record<string, unknown> | null;
    ip_address: string | null;
    request_path: string | null;
    created_at: string;
}
