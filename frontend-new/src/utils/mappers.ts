/**
 * BE → FE Data Mappers
 * Auto-generated from data contract analysis
 * 
 * Usage:
 *   import { mapProcessToEventLog, mapDFGResponse } from './mappers';
 *   const feData = mapProcessToEventLog(beResponse);
 */

// =============================================================================
// Backend Types (from schemas.py)
// =============================================================================

export interface BEProcessResponse {
  id: string;
  name: string;
  source_format: string;
  total_events: number;
  total_cases: number;
  total_activities: number;
  activities: string[];
  created_at: string;
  source_file?: string; // Now included in BE response
}

export interface BEDFGNode {
  id: string;
  name: string;
  frequency: number;
  is_start: boolean;
  is_end: boolean;
}

export interface BEDFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avg_duration_seconds?: number;
  min_duration_seconds?: number;
  max_duration_seconds?: number;
}

export interface BEDFGResponse {
  nodes: BEDFGNode[];
  edges: BEDFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_frequency: number;
}

export interface BEVariantResponse {
  variant_key: string;
  activity_trace: string;
  case_count: number;
  frequency_percent: number;
  avg_duration_seconds: number | null;
  complexity_score?: number;
  rework_count?: number;
  unique_activity_count?: number;
}

export interface BEActivityDetailResponse {
  activity: string;
  frequency: number;
  frequency_percent: number;
  avg_duration_seconds: number | null;
  min_duration_seconds: number | null;
  max_duration_seconds: number | null;
  is_start_activity: boolean;
  is_end_activity: boolean;
  position_avg: number | null;
  resources: string[]; // Now included in BE response
}

export interface BEBottleneckResponse {
  activity: string;
  avg_waiting_time_seconds: number;
  avg_service_time_seconds: number;
  frequency: number;
  is_bottleneck: boolean;
  severity: 'low' | 'medium' | 'high';
}

export interface BEStatisticsResponse {
  total_events: number;
  total_cases: number;
  total_activities: number;
  total_variants: number;
  activities: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  avg_case_duration_seconds: number | null;
  min_case_duration_seconds: number | null;
  max_case_duration_seconds: number | null;
  date_range: { start: string; end: string } | null;
}

export interface BEFilterOptionsResponse {
  activities: string[];
  resources: string[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_variants: number;
  time_range: { start: string | null; end: string | null };
  case_size_range: { min: number; max: number };
}

// =============================================================================
// Frontend Types (from mockExplorerData.ts and page components)
// =============================================================================

export interface FEEventLog {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  createdAt: string;
  sourceFile?: string;
}

export interface FEDFGNode {
  id: string;
  label: string;
  frequency: number;
}

export interface FEDFGEdge {
  source: string;
  target: string;
  frequency: number;
  performance?: number;
}

export interface FEDFGResponse {
  log_id: string;
  nodes: FEDFGNode[];
  edges: FEDFGEdge[];
  start_activities: Record<string, number>;
  end_activities: Record<string, number>;
  total_cases: number;
}

export interface FEVariant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDurationSeconds: number;
  isHappyPath?: boolean;
}

export interface FEActivityDetail {
  id: string;
  name: string;
  totalOccurrences: number;
  casePercentage: number;
  avgDurationSeconds: number;
  minDurationSeconds: number;
  maxDurationSeconds: number;
  resources: string[]; // Note: Not available in BE, must be populated separately
}

export interface FEBottleneck {
  activity: string;
  avgDuration: number;
  frequency: number;
  impact: number;
}

export interface FEFilterOptions {
  activities: string[];
  resources: string[];
  timeRange: { start: string; end: string };
  caseDuration: { min: number; max: number; mean: number };
}

// =============================================================================
// Mapper Functions
// =============================================================================

/**
 * Maps BE ProcessResponse to FE EventLog
 */
export function mapProcessToEventLog(be: BEProcessResponse): FEEventLog {
  return {
    id: be.id,
    name: be.name,
    totalCases: be.total_cases,
    totalEvents: be.total_events,
    createdAt: be.created_at,
    sourceFile: be.source_file, // Now available from BE
  };
}

/**
 * Maps BE DFG Response to FE format
 * @param logId - Must be injected from request context
 */
export function mapDFGResponse(be: BEDFGResponse, logId: string): FEDFGResponse {
  return {
    log_id: logId,
    nodes: be.nodes.map((node) => ({
      id: node.id,
      label: node.name,
      frequency: node.frequency,
    })),
    edges: be.edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency,
      performance: edge.avg_duration_seconds,
    })),
    start_activities: be.start_activities,
    end_activities: be.end_activities,
    total_cases: be.total_frequency,
  };
}

/**
 * Maps BE variants to FE format
 * Computes isHappyPath based on highest case count
 */
export function mapVariants(variants: BEVariantResponse[]): FEVariant[] {
  const maxCaseCount = Math.max(...variants.map((v) => v.case_count), 0);

  return variants.map((v) => ({
    key: v.variant_key,
    activities: v.activity_trace.split(' -> '),
    caseCount: v.case_count,
    frequencyPercent: v.frequency_percent,
    avgDurationSeconds: v.avg_duration_seconds ?? 0,
    isHappyPath: v.case_count === maxCaseCount,
  }));
}

/**
 * Maps BE activity details to FE format
 * Note: resources field must be populated separately
 */
export function mapActivityDetails(
  activities: BEActivityDetailResponse[]
): FEActivityDetail[] {
  return activities.map((a) => ({
    id: a.activity,
    name: a.activity,
    totalOccurrences: a.frequency,
    casePercentage: a.frequency_percent,
    avgDurationSeconds: a.avg_duration_seconds ?? 0,
    minDurationSeconds: a.min_duration_seconds ?? 0,
    maxDurationSeconds: a.max_duration_seconds ?? 0,
    resources: a.resources, // Now available from BE
  }));
}

/**
 * Severity to impact score mapping
 */
const SEVERITY_TO_IMPACT: Record<string, number> = {
  high: 95,
  medium: 65,
  low: 32,
};

/**
 * Maps BE bottlenecks to FE format
 * Combines waiting + service time into avgDuration
 * Converts severity to numeric impact score
 */
export function mapBottlenecks(bottlenecks: BEBottleneckResponse[]): FEBottleneck[] {
  return bottlenecks.map((b) => ({
    activity: b.activity,
    avgDuration: b.avg_waiting_time_seconds + b.avg_service_time_seconds,
    frequency: b.frequency,
    impact: SEVERITY_TO_IMPACT[b.severity] ?? 50,
  }));
}

/**
 * Maps BE filter options to FE format
 */
export function mapFilterOptions(be: BEFilterOptionsResponse): FEFilterOptions {
  const min = be.case_size_range.min;
  const max = be.case_size_range.max;

  return {
    activities: be.activities,
    resources: be.resources,
    timeRange: {
      start: be.time_range.start ?? new Date(0).toISOString(),
      end: be.time_range.end ?? new Date().toISOString(),
    },
    caseDuration: {
      min,
      max,
      mean: (min + max) / 2, // Approximation
    },
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Converts snake_case keys to camelCase recursively
 */
export function snakeToCamelKeys<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map(snakeToCamelKeys) as T;
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj).map(([key, value]) => [
        key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase()),
        snakeToCamelKeys(value),
      ])
    ) as T;
  }
  return obj as T;
}

/**
 * Null-safe number accessor with default
 */
export function safeNumber(value: number | null | undefined, defaultValue = 0): number {
  return value ?? defaultValue;
}

/**
 * Format duration from seconds to human-readable string
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  }
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)}m`;
  }
  if (seconds < 86400) {
    return `${(seconds / 3600).toFixed(1)}h`;
  }
  return `${(seconds / 86400).toFixed(1)}d`;
}
