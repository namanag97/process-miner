/**
 * Analytics Types for Process Mining SDK
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// DASHBOARD
// =============================================================================

export interface DashboardData extends HypermediaResponse {
  logId: string;
  overview: {
    totalCases: number;
    totalEvents: number;
    uniqueActivities: number;
    uniqueResources: number;
    avgCaseDuration: number;
    medianCaseDuration: number;
  };
  topVariants: Array<{
    activities: string[];
    count: number;
    percentage: number;
  }>;
  activityDistribution: Record<string, number>;
  timeDistribution: Array<{
    period: string;
    caseCount: number;
    eventCount: number;
  }>;
}

// =============================================================================
// INSIGHTS
// =============================================================================

export type InsightSeverity = "info" | "warning" | "critical";
export type InsightCategory = "performance" | "conformance" | "resource" | "variant";

export interface ProcessInsight extends HypermediaResponse {
  id: string;
  category: InsightCategory;
  severity: InsightSeverity;
  title: string;
  description: string;
  metric?: number;
  recommendation?: string;
}

// =============================================================================
// ANOMALIES
// =============================================================================

export interface AnomalousCase extends HypermediaResponse {
  caseId: string;
  anomalyType: string;
  score: number;
  details: string;
  activities: string[];
}

export interface AnomalyAnalysis extends HypermediaResponse {
  logId: string;
  totalAnomalies: number;
  anomalyRate: number;
  cases: AnomalousCase[];
}

// =============================================================================
// VARIANT STATS
// =============================================================================

export interface VariantStatistics extends HypermediaResponse {
  logId: string;
  totalVariants: number;
  topVariants: Array<{
    rank: number;
    activities: string[];
    caseCount: number;
    percentage: number;
    avgDuration?: number;
  }>;
  variantDistribution: {
    singleCaseVariants: number;
    multiCaseVariants: number;
    coverageTop5: number;
    coverageTop10: number;
  };
}

// =============================================================================
// RESOURCE STATS
// =============================================================================

export interface ResourceStatistics extends HypermediaResponse {
  logId: string;
  totalResources: number;
  resources: Array<{
    name: string;
    eventCount: number;
    caseCount: number;
    avgEventsPerCase: number;
    activities: string[];
  }>;
}

// =============================================================================
// TIME ANALYSIS
// =============================================================================

export interface TimeAnalysis extends HypermediaResponse {
  logId: string;
  dateRange: {
    start: string;
    end: string;
  };
  casesOverTime: Array<{
    period: string;
    count: number;
  }>;
  avgDurationOverTime: Array<{
    period: string;
    avgDuration: number;
  }>;
  peakHours?: number[];
  peakDays?: string[];
}

// =============================================================================
// PERFORMANCE METRICS (used by AnalyticsClient)
// Aligned with backend schemas.py
// =============================================================================

export interface Bottleneck {
  activity: string;
  avgWaitingTime: number;
  avgServiceTime: number;
  frequency: number;
  isBottleneck: boolean;
  severity: "low" | "medium" | "high";
  impactScore: number;
}

export interface BottleneckListResponse extends HypermediaResponse {
  logId: string;
  bottlenecks: Bottleneck[];
  totalBottlenecks: number;
}

export interface ReworkActivity {
  activity: string;
  reworkCount: number;
  casesWithRework: number;
  reworkPercentage: number;
}

export interface ReworkListResponse extends HypermediaResponse {
  logId: string;
  reworkActivities: ReworkActivity[];
  totalReworkCases: number;
  reworkPercentage: number;
}

export interface ServiceTimeResponse {
  activity: string;
  minSeconds: number;
  maxSeconds: number;
  avgSeconds: number;
  medianSeconds: number;
  stdDevSeconds: number;
}

export interface CycleTimeResponse extends HypermediaResponse {
  logId: string;
  minSeconds: number;
  maxSeconds: number;
  avgSeconds: number;
  medianSeconds: number;
  percentile25: number;
  percentile75: number;
  percentile95: number;
}

export interface ThroughputResponse extends HypermediaResponse {
  logId: string;
  totalCases: number;
  completedCases: number;
  casesPerDay: number;
  casesPerWeek: number;
  casesPerMonth: number;
  timeRangeDays: number;
}

export interface PatternResponse {
  pattern: string;
  frequency: number;
  support: number;
}

/**
 * Performance data used by FE PerformanceTab
 * Matches what getPerformance() returns after transformation
 */
export interface PerformanceData extends HypermediaResponse {
  logId: string;
  cycleTime: CycleTimeResponse;
  throughput: ThroughputResponse;
  topBottlenecks: Array<{
    activity: string;
    avgWaitingTime: number;
    impactScore: number;
  }>;
  reworkSummary: {
    totalReworkCases: number;
    reworkPercentage: number;
  };
}

export interface PerformanceDashboardResponse extends HypermediaResponse {
  logId: string;
  cycleTime: CycleTimeResponse;
  throughput: ThroughputResponse;
  topBottlenecks: Bottleneck[];
  reworkSummary: Record<string, unknown>;
}
