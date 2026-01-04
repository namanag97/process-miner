/**
 * Explorer Feature Types
 *
 * Type definitions for process explorer entities including
 * DFG nodes, edges, variants, and activities.
 *
 * NOTE: SDK types are available at @frontend-new/openapi-sdk for API validation.
 * Frontend uses camelCase conventions while SDK uses snake_case from backend.
 */

// ============================================
// SDK Types for Reference/Validation
// ============================================

export type {
  DFGNode as SDKDFGNode,
  DFGEdge as SDKDFGEdge,
  DFGResponse as SDKDFGResponse,
  VariantResponse as SDKVariantResponse,
  ActivityDetailResponse as SDKActivityDetail,
  StatisticsResponse as SDKStatisticsResponse,
  FilterOptionsResponse as SDKFilterOptions,
} from '@frontend-new/openapi-sdk';

// ============================================
// DFG Types (frontend shape)
// ============================================

export interface DFGNode {
  id: string;
  label: string;
  frequency: number;
  isStart: boolean;
  isEnd: boolean;
}

export interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability?: number;
  avgDuration?: number;
}

export interface DFGResponse {
  nodes: DFGNode[];
  edges: DFGEdge[];
  stats?: DFGStats;
}

export interface DFGStats {
  totalCases: number;
  totalActivities: number;
  totalTransitions: number;
}

// ============================================
// Variant Types
// ============================================

export interface Variant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDuration: number | null;
  complexityScore?: number;
}

export interface ProcessedVariant extends Variant {
  isHappyPath: boolean;
  hasRework: boolean;
  avgDurationSeconds: number;
  conformanceScore?: number;
}

// ============================================
// Activity Types
// ============================================

export interface ActivityDetail {
  id: string;
  name: string;
  frequency: number;
  frequencyPercent: number;
  avgDuration: number | null;
  minDuration: number | null;
  maxDuration: number | null;
  isStart: boolean;
  isEnd: boolean;
  resources: string[];
}

export interface ActivityData {
  id: string;
  name: string;
  totalOccurrences: number;
  casePercentage: number;
  avgDurationSeconds: number;
  minDurationSeconds: number;
  maxDurationSeconds: number;
  resources: string[];
}

// ============================================
// Edge Types
// ============================================

export interface EdgeDetail {
  id: string;
  source: string;
  target: string;
  frequency: number;
  frequencyPercent: number;
  avgDurationSeconds?: number;
}

// ============================================
// Canvas Types (for ProcessCanvas component)
// ============================================

export interface DFGNodeData {
  id: string;
  label: string;
  frequency: number;
  isStart?: boolean;
  isEnd?: boolean;
  avgDuration?: number;
  minDuration?: number;
  maxDuration?: number;
}

export interface DFGEdgeData {
  source: string;
  target: string;
  frequency: number;
  performance?: number;
}

export type MetricMode = 'frequency' | 'performance';

// ============================================
// Filter Types
// ============================================

export type FilterType =
  | 'timeRange'
  | 'activity'
  | 'activitySequence'
  | 'performance'
  | 'resource'
  | 'variant'
  | 'rework';

export interface AppliedFilter {
  id: string;
  type: FilterType;
  label: string;
  value: unknown;
  color?: string;
}

export interface FilterOptions {
  activities: string[];
  resources: string[];
  timeRange: { start: string; end: string };
  caseDuration: { min: number; max: number; mean: number; p90?: number };
  variantCount?: number;
}

// ============================================
// KPI Types
// ============================================

export interface ProcessKPIs {
  totalCases: number;
  uniqueVariants: number;
  uniqueActivities: number;
  avgThroughputTime?: number;
  happyPathPercent?: number;
  reworkRate?: number;
}

// ============================================
// Query Options
// ============================================

export interface DFGBuildOptions {
  includePerformance?: boolean;
  activityThreshold?: number;
  pathThreshold?: number;
}

export interface VariantOptions {
  topN?: number;
  includeComplexity?: boolean;
}

// ============================================
// Utility Functions
// ============================================

export function hasReworkInVariant(activities: string[]): boolean {
  const seen = new Set<string>();
  for (const activity of activities) {
    if (seen.has(activity)) return true;
    seen.add(activity);
  }
  return false;
}

export function toProcessedVariant(variant: Variant, index: number): ProcessedVariant {
  return {
    ...variant,
    avgDurationSeconds: variant.avgDuration ?? 0,
    isHappyPath: index === 0 && variant.frequencyPercent > 50,
    hasRework: hasReworkInVariant(variant.activities),
  };
}

export function toActivityData(activity: ActivityDetail): ActivityData {
  return {
    id: activity.id,
    name: activity.name,
    totalOccurrences: activity.frequency,
    casePercentage: activity.frequencyPercent,
    avgDurationSeconds: activity.avgDuration ?? 0,
    minDurationSeconds: activity.minDuration ?? 0,
    maxDurationSeconds: activity.maxDuration ?? 0,
    resources: activity.resources,
  };
}
