/**
 * Transformers - Convert backend snake_case responses to frontend camelCase
 */

import type {
  ProcessResponse,
  ProcessDetailResponse,
  ColumnDetectionResponse,
  DFGResponse,
  DFGNodeResponse,
  DFGEdgeResponse,
  VariantResponse,
  ActivityDetailResponse,
  PerformanceDashboardResponse,
  ReworkListResponse,
  BottleneckResponse,
  OCELLogResponse,
  OCELStatisticsResponse,
} from './types';

// ============================================
// Frontend Types (camelCase)
// ============================================

export interface EventLog {
  id: string;
  name: string;
  sourceFormat: string;
  totalEvents: number;
  totalCases: number;
  totalActivities: number;
  activities: string[];
  createdAt: string;
  sourceFile?: string;
  status?: string; // Dataset status: 'unstructured' | 'ready' | 'analyzing' | 'error'
  statistics?: Record<string, unknown>;
  updatedAt?: string;
}

export interface ColumnDetection {
  columns: string[];
  suggestions: {
    caseId?: string;
    activity?: string;
    timestamp?: string;
    resource?: string;
  };
  sampleRows: Record<string, unknown>[];
  rowCount: number;
}

export interface DFGNode {
  id: string;
  label: string;
  frequency: number;
  isStart: boolean;
  isEnd: boolean;
}

export interface DFGEdge {
  id: string;
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avgDuration?: number;
  minDuration?: number;
  maxDuration?: number;
}

export interface DFGData {
  nodes: DFGNode[];
  edges: DFGEdge[];
  startActivities: Record<string, number>;
  endActivities: Record<string, number>;
  totalFrequency: number;
}

export interface Variant {
  key: string;
  activityTrace: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDuration?: number;
  complexityScore?: number;
  reworkCount?: number;
}

export interface ActivityDetail {
  id: string;
  name: string;
  frequency: number;
  frequencyPercent: number;
  avgDuration?: number;
  minDuration?: number;
  maxDuration?: number;
  isStartActivity: boolean;
  isEndActivity: boolean;
  positionAvg?: number;
  resources: string[];
}

export interface PerformanceData {
  logId: string;
  cycleTime: {
    minSeconds: number;
    maxSeconds: number;
    avgSeconds: number;
    medianSeconds: number;
    percentile25: number;
    percentile75: number;
    percentile95: number;
  };
  throughput: {
    totalCases: number;
    completedCases: number;
    casesPerDay: number;
    casesPerWeek: number;
    casesPerMonth: number;
    timeRangeDays: number;
  };
  topBottlenecks: Array<{
    activity: string;
    avgWaitingTime: number;
    avgServiceTime: number;
    frequency: number;
    isBottleneck: boolean;
    severity: string;
    impactScore: number;
  }>;
  reworkSummary: Record<string, unknown>;
}

export interface ReworkData {
  logId: string;
  reworkActivities: Array<{
    activity: string;
    reworkCount: number;
    casesWithRework: number;
    reworkPercentage: number;
  }>;
  totalReworkCases: number;
  reworkPercentage: number;
}

export interface OCELLog {
  id: string;
  name: string;
  sourceFile?: string;
  sourceFormat: string;
  totalEvents: number;
  totalObjects: number;
  totalObjectTypes: number;
  objectTypes: string[];
  activities: string[];
  createdAt: string;
}

export interface OCELStatistics {
  logId: string;
  totalEvents: number;
  totalObjects: number;
  totalObjectTypes: number;
  totalActivities: number;
  objectTypes: string[];
  activities: string[];
  objectsPerType: Record<string, number>;
}

// ============================================
// Transform Functions
// ============================================

export function transformProcess(be: ProcessResponse): EventLog {
  return {
    id: be.id,
    name: be.name,
    sourceFormat: be.source_format,
    totalEvents: be.total_events,
    totalCases: be.total_cases,
    totalActivities: be.total_activities,
    activities: be.activities,
    createdAt: be.created_at,
    sourceFile: be.source_file,
    status: be.status,
  };
}

export function transformProcessDetail(be: ProcessDetailResponse): EventLog {
  return {
    ...transformProcess(be),
    statistics: be.statistics,
    updatedAt: be.updated_at,
  };
}

export function transformColumnDetection(be: ColumnDetectionResponse): ColumnDetection {
  const s = be.suggestions as Record<string, string | undefined>;
  return {
    columns: be.columns,
    suggestions: {
      caseId: s.case_id_column ?? s.case_id,
      activity: s.activity_column ?? s.activity,
      timestamp: s.timestamp_column ?? s.timestamp,
      resource: s.resource_column ?? s.resource,
    },
    sampleRows: be.sample_rows,
    rowCount: be.row_count,
  };
}

export function transformDFGNode(be: DFGNodeResponse): DFGNode {
  return {
    id: be.id,
    label: be.name,
    frequency: be.frequency,
    isStart: be.is_start,
    isEnd: be.is_end,
  };
}

export function transformDFGEdge(be: DFGEdgeResponse, index: number): DFGEdge {
  return {
    id: `edge-${be.source}-${be.target}-${index}`,
    source: be.source,
    target: be.target,
    frequency: be.frequency,
    probability: be.probability,
    avgDuration: be.avg_duration_seconds,
    minDuration: be.min_duration_seconds,
    maxDuration: be.max_duration_seconds,
  };
}

export function transformDFG(be: DFGResponse): DFGData {
  return {
    nodes: be.nodes.map(transformDFGNode),
    edges: be.edges.map((e, i) => transformDFGEdge(e, i)),
    startActivities: be.start_activities,
    endActivities: be.end_activities,
    totalFrequency: be.total_frequency,
  };
}

export function transformVariant(be: VariantResponse): Variant {
  // Backend now sends pre-parsed activities array - use it directly
  let activities: string[] = be.activities || [];

  // Fallback: If backend doesn't send activities array (backwards compatibility),
  // parse from activity_trace string
  if (activities.length === 0 && be.activity_trace) {
    const separators = ['→', '->', ' -> ', ','];

    for (const sep of separators) {
      if (be.activity_trace.includes(sep)) {
        activities = be.activity_trace
          .split(sep)
          .map(a => a.trim())
          .filter(Boolean);
        break;
      }
    }

    // Fallback: if no separator found, treat as single activity
    if (activities.length === 0 && be.activity_trace.trim()) {
      activities = [be.activity_trace.trim()];
    }
  }

  return {
    key: be.variant_key,
    activityTrace: be.activity_trace,
    activities,
    caseCount: be.case_count,
    frequencyPercent: be.frequency_percent,
    avgDuration: be.avg_duration_seconds,
    complexityScore: be.complexity_score,
    reworkCount: be.rework_count,
  };
}

export function transformVariants(be: VariantResponse[]): Variant[] {
  return be.map(transformVariant);
}

export function transformActivityDetail(be: ActivityDetailResponse): ActivityDetail {
  return {
    id: be.activity,
    name: be.activity,
    frequency: be.frequency,
    frequencyPercent: be.frequency_percent,
    avgDuration: be.avg_duration_seconds,
    minDuration: be.min_duration_seconds,
    maxDuration: be.max_duration_seconds,
    isStartActivity: be.is_start_activity,
    isEndActivity: be.is_end_activity,
    positionAvg: be.position_avg,
    resources: be.resources,
  };
}

export function transformActivityDetails(be: ActivityDetailResponse[]): ActivityDetail[] {
  return be.map(transformActivityDetail);
}

export function transformBottleneck(be: BottleneckResponse) {
  return {
    activity: be.activity,
    avgWaitingTime: be.avg_waiting_time_seconds,
    avgServiceTime: be.avg_service_time_seconds,
    frequency: be.frequency,
    isBottleneck: be.is_bottleneck,
    severity: be.severity,
    impactScore: be.bottleneck_impact_score,
  };
}

export function transformPerformance(be: PerformanceDashboardResponse): PerformanceData {
  return {
    logId: be.log_id,
    cycleTime: {
      minSeconds: be.cycle_time.min_seconds,
      maxSeconds: be.cycle_time.max_seconds,
      avgSeconds: be.cycle_time.avg_seconds,
      medianSeconds: be.cycle_time.median_seconds,
      percentile25: be.cycle_time.percentile_25_seconds,
      percentile75: be.cycle_time.percentile_75_seconds,
      percentile95: be.cycle_time.percentile_95_seconds,
    },
    throughput: {
      totalCases: be.throughput.total_cases,
      completedCases: be.throughput.completed_cases,
      casesPerDay: be.throughput.cases_per_day,
      casesPerWeek: be.throughput.cases_per_week,
      casesPerMonth: be.throughput.cases_per_month,
      timeRangeDays: be.throughput.time_range_days,
    },
    topBottlenecks: be.top_bottlenecks.map(transformBottleneck),
    reworkSummary: be.rework_summary,
  };
}

export function transformRework(be: ReworkListResponse): ReworkData {
  return {
    logId: be.log_id,
    reworkActivities: be.rework_activities.map(r => ({
      activity: r.activity,
      reworkCount: r.rework_count,
      casesWithRework: r.cases_with_rework,
      reworkPercentage: r.rework_percentage,
    })),
    totalReworkCases: be.total_rework_cases,
    reworkPercentage: be.rework_percentage,
  };
}

export function transformOCELLog(be: OCELLogResponse): OCELLog {
  return {
    id: be.id,
    name: be.name,
    sourceFile: be.source_file,
    sourceFormat: be.source_format,
    totalEvents: be.total_events,
    totalObjects: be.total_objects,
    totalObjectTypes: be.total_object_types,
    objectTypes: be.object_types,
    activities: be.activities,
    createdAt: be.created_at,
  };
}

export function transformOCELStatistics(be: OCELStatisticsResponse): OCELStatistics {
  return {
    logId: be.log_id,
    totalEvents: be.total_events,
    totalObjects: be.total_objects,
    totalObjectTypes: be.total_object_types,
    totalActivities: be.total_activities,
    objectTypes: be.object_types,
    activities: be.activities,
    objectsPerType: be.objects_per_type,
  };
}
