/**
 * Performance Analysis Types for Process Mining SDK
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// PERFORMANCE RESULTS
// =============================================================================

export interface PerformanceSummary extends HypermediaResponse {
  logId: string;
  avgCaseDuration: number;
  medianCaseDuration: number;
  minCaseDuration: number;
  maxCaseDuration: number;
  stdDevCaseDuration?: number;
  totalCases: number;
  totalEvents: number;
  avgEventsPerCase: number;
}

export interface ActivityPerformance {
  activity: string;
  count: number;
  avgDuration: number;
  medianDuration: number;
  minDuration: number;
  maxDuration: number;
  avgWaitTime?: number;
  avgServiceTime?: number;
}

export interface TransitionPerformance {
  source: string;
  target: string;
  count: number;
  avgDuration: number;
  medianDuration: number;
  minDuration: number;
  maxDuration: number;
}

// =============================================================================
// BOTTLENECKS
// =============================================================================

export type BottleneckSeverity = "low" | "medium" | "high" | "critical";

export interface Bottleneck extends HypermediaResponse {
  type: "activity" | "transition";
  name: string;
  severity: BottleneckSeverity;
  avgDuration: number;
  medianDuration: number;
  frequency: number;
  impactScore: number;
  recommendation?: string;
}

export interface BottleneckAnalysis extends HypermediaResponse {
  logId: string;
  bottlenecks: Bottleneck[];
  totalBottlenecks: number;
  criticalCount: number;
  highCount: number;
  mediumCount: number;
  lowCount: number;
}

// =============================================================================
// DURATION HISTOGRAM
// =============================================================================

export interface HistogramBucket {
  rangeStart: number;
  rangeEnd: number;
  count: number;
  percentage: number;
}

export interface DurationHistogram extends HypermediaResponse {
  logId: string;
  buckets: HistogramBucket[];
  totalCases: number;
  avgDuration: number;
  medianDuration: number;
}
