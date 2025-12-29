/**
 * Filtering Types - Event Log Filtering
 *
 * TODO: These types should be auto-generated from OpenAPI spec
 * For now, they match the backend Pydantic schemas
 */

export interface FilterConfig {
  type: string;
  params: Record<string, any>;
}

export interface FilterRequest {
  filters: FilterConfig[];
  name?: string;
  save_result?: boolean;
}

export interface FilterPreviewRequest {
  filters: FilterConfig[];
}

export interface FilterStatistics {
  original_cases: number;
  filtered_cases: number;
  original_events: number;
  filtered_events: number;
  cases_removed: number;
  events_removed: number;
  removal_percentage: number;
}

export interface FilteredLogResponse {
  filtered_log_id?: string;
  source_log_id: string;
  name?: string;
  filters_applied: FilterConfig[];
  statistics: FilterStatistics;
  created_at?: string;
}

export interface FilterPreviewResponse {
  source_log_id: string;
  statistics: FilterStatistics;
  sample_removed_cases?: string[];
}

export interface FilterOptionsResponse {
  log_id: string;
  activities: string[];
  resources: string[];
  variants: Array<{ variant: string; count: number }>;
  time_range: {
    start: string;
    end: string;
  };
  case_duration: {
    min: number;
    max: number;
    mean: number;
  };
}

export interface FilteredLogListResponse {
  source_log_id: string;
  filtered_logs: FilteredLogResponse[];
  total: number;
}

export interface FilterTemplateResponse {
  id: string;
  name: string;
  description: string;
  filters: FilterConfig[];
  category: string;
}

export interface FilterTemplateListResponse {
  templates: FilterTemplateResponse[];
  total: number;
}
