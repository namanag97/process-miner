/**
 * Transformers - Convert backend snake_case responses to frontend camelCase
 */

import type {
  ProcessResponse,
  ProcessDetailResponse,
  DFGResponse,
  DFGNodeResponse,
  DFGEdgeResponse,
  VariantResponse,
  ActivityDetailResponse,
  PerformanceDashboardResponse,
  ReworkListResponse,
  BottleneckResponse,
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
  statistics?: Record<string, unknown>;
  updatedAt?: string;
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
  };
}

export function transformProcessDetail(be: ProcessDetailResponse): EventLog {
  return {
    ...transformProcess(be),
    statistics: be.statistics,
    updatedAt: be.updated_at,
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
  // Parse activity trace like "Create→Approve→Ship" into array (BUG-008 fix)
  const activities = be.activity_trace
    ? be.activity_trace.split('→').map(a => a.trim()).filter(Boolean)
    : [];
  
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
