/**
 * API Types - TypeScript interfaces matching backend Pydantic schemas
 * All types use snake_case to match backend responses
 */

// ============================================
// Common
// ============================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

// ============================================
// Event Logs / Processes
// ============================================

export interface ProcessResponse {
  id: string;
  name: string;
  source_format: string;
  total_events: number;
  total_cases: number;
  total_activities: number;
  activities: string[];
  created_at: string;
  source_file?: string;
}

export interface ProcessDetailResponse extends ProcessResponse {
  statistics?: Record<string, unknown>;
  updated_at?: string;
}

export interface ColumnDetectionResponse {
  columns: string[];
  suggestions: {
    case_id?: string;
    activity?: string;
    timestamp?: string;
    resource?: string;
  };
  sample_rows: Record<string, unknown>[];
  row_count: number;
}

export interface StatisticsResponse {
  total_events: number;
  total_cases: number;
  total_activities: number;
  total_variants: number;
  activities: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  avg_case_duration_seconds?: number;
  min_case_duration_seconds?: number;
  max_case_duration_seconds?: number;
  date_range?: { start: string; end: string };
}

// ============================================
// Visualization / DFG
// ============================================

export interface DFGNodeResponse {
  id: string;
  name: string;
  frequency: number;
  is_start: boolean;
  is_end: boolean;
}

export interface DFGEdgeResponse {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
}

export interface DFGResponse {
  nodes: DFGNodeResponse[];
  edges: DFGEdgeResponse[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_frequency: number;
}

// ============================================
// Variants & Activities
// ============================================

export interface VariantResponse {
  variant_key: string;
  activity_trace: string;
  case_count: number;
  frequency_percent: number;
  avg_duration_seconds?: number;
  complexity_score?: number;
  rework_count?: number;
  unique_activity_count?: number;
}

export interface ActivityDetailResponse {
  activity: string;
  frequency: number;
  frequency_percent: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
  is_start_activity: boolean;
  is_end_activity: boolean;
  position_avg?: number;
  resources: string[];
}

// ============================================
// Analytics
// ============================================

export interface BottleneckResponse {
  activity: string;
  avg_waiting_time_seconds: number;
  avg_service_time_seconds: number;
  frequency: number;
  is_bottleneck: boolean;
  severity: string;
  preceding_activities: string[];
  following_activities: string[];
  bottleneck_impact_score: number;
}

export interface ReworkResponse {
  activity: string;
  rework_count: number;
  cases_with_rework: number;
  rework_percentage: number;
}

export interface ReworkListResponse {
  log_id: string;
  rework_activities: ReworkResponse[];
  total_rework_cases: number;
  rework_percentage: number;
}

export interface CycleTimeResponse {
  log_id: string;
  min_seconds: number;
  max_seconds: number;
  avg_seconds: number;
  median_seconds: number;
  percentile_25_seconds: number;
  percentile_75_seconds: number;
  percentile_95_seconds: number;
}

export interface ThroughputResponse {
  log_id: string;
  total_cases: number;
  completed_cases: number;
  cases_per_day: number;
  cases_per_week: number;
  cases_per_month: number;
  time_range_days: number;
}

export interface PerformanceDashboardResponse {
  log_id: string;
  cycle_time: CycleTimeResponse;
  throughput: ThroughputResponse;
  top_bottlenecks: BottleneckResponse[];
  rework_summary: Record<string, unknown>;
}

// ============================================
// Conformance
// ============================================

export interface ConformanceResponse {
  id: string;
  log_id: string;
  model_id: string;
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  method: string;
  is_conformant: boolean;
  fitting_traces: number;
  total_traces: number;
  created_at: string;
}

export interface DeviationDetail {
  case_id: string;
  activity: string;
  violation_type: string;
  expected_after?: string;
  frequency: number;
  impact: string;
}

export interface DiagnosticsResponse {
  fitness: number;
  precision?: number;
  generalization?: number;
  simplicity?: number;
  total_traces: number;
  fitting_traces: number;
  non_fitting_traces: number;
  fitness_ratio: number;
  deviations?: DeviationDetail[];
}

// ============================================
// Predictions
// ============================================

export interface PredictorResponse {
  id: string;
  log_id: string;
  target_type: string;
  algorithm: string;
  metrics?: Record<string, number>;
  trained_at?: string;
}

export interface PredictionResponse {
  predictor_id: string;
  case_prefix: string[];
  prediction: string;
  confidence: number;
  alternatives?: Array<{ activity: string; probability: number }>;
}
