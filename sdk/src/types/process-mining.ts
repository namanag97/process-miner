/**
 * Process Mining Types - PM4Py Advanced Features
 */

import { HypermediaResponse } from "./common.js";

// =============================================================================
// FOOTPRINTS
// =============================================================================

export interface FootprintMatrix extends HypermediaResponse {
  logId: string;
  activities: string[];
  matrix: Record<string, Record<string, string>>;
  relations: {
    directlyFollows: Array<[string, string]>;
    causal: Array<[string, string]>;
    parallel: Array<[string, string]>;
    choice: Array<[string, string]>;
  };
}

// =============================================================================
// LOG SKELETON
// =============================================================================

export interface LogSkeleton extends HypermediaResponse {
  logId: string;
  activities: string[];
  equivalences: Array<[string, string]>;
  alwaysAfter: Array<[string, string]>;
  alwaysBefore: Array<[string, string]>;
  neverTogether: Array<[string, string]>;
  directlyFollows: Array<[string, string]>;
  activityCount: Record<string, { min: number; max: number }>;
}

// =============================================================================
// SOCIAL NETWORK ANALYSIS
// =============================================================================

export interface SNAResult extends HypermediaResponse {
  logId: string;
  metric: string;
  nodes: Array<{
    resource: string;
    value: number;
  }>;
  edges?: Array<{
    source: string;
    target: string;
    weight: number;
  }>;
}

// =============================================================================
// BATCH DETECTION
// =============================================================================

export interface BatchPattern extends HypermediaResponse {
  activity: string;
  batchType: "simultaneous" | "sequential" | "concurrent";
  caseCount: number;
  avgBatchSize: number;
}

// =============================================================================
// TRANSITION SYSTEM
// =============================================================================

export interface TransitionSystemState {
  id: string;
  label: string;
  isStart: boolean;
  isEnd: boolean;
}

export interface TransitionSystemTransition {
  source: string;
  target: string;
  label: string;
  frequency: number;
}

export interface TransitionSystem extends HypermediaResponse {
  logId: string;
  states: TransitionSystemState[];
  transitions: TransitionSystemTransition[];
}

// =============================================================================
// DURATION STATS
// =============================================================================

export interface DurationStats extends HypermediaResponse {
  logId: string;
  avgDuration: number;
  medianDuration: number;
  minDuration: number;
  maxDuration: number;
  stdDev: number;
  percentiles: Record<string, number>;
}

// =============================================================================
// ARRIVAL RATE
// =============================================================================

export interface ArrivalRate extends HypermediaResponse {
  logId: string;
  avgArrivalRate: number;
  unit: string;
  casesPerDay?: number;
  casesPerHour?: number;
}

// =============================================================================
// COMPREHENSIVE ANALYSIS
// =============================================================================

export interface ComprehensiveAnalysis extends HypermediaResponse {
  logId: string;
  summary: {
    totalCases: number;
    totalEvents: number;
    totalActivities: number;
    totalVariants: number;
    avgCaseDuration: number;
  };
  startActivities: Record<string, number>;
  endActivities: Record<string, number>;
  variants: Array<{
    activities: string[];
    count: number;
  }>;
}
