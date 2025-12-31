/**
 * Explorer Feature Types
 *
 * Type definitions for process explorer entities including
 * DFG nodes, edges, variants, and activities.
 */

// ============================================
// DFG Types
// ============================================

/**
 * DFG Node data from SDK
 */
export interface DFGNode {
  id: string;
  label: string;
  frequency: number;
  isStart: boolean;
  isEnd: boolean;
}

/**
 * DFG Edge data from SDK
 */
export interface DFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability?: number;
  avgDuration?: number;
}

/**
 * Complete DFG response from SDK
 */
export interface DFGResponse {
  nodes: DFGNode[];
  edges: DFGEdge[];
  stats?: DFGStats;
}

/**
 * DFG statistics
 */
export interface DFGStats {
  totalCases: number;
  totalActivities: number;
  totalTransitions: number;
}

// ============================================
// Variant Types
// ============================================

/**
 * Process variant from SDK
 */
export interface Variant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDuration: number | null;
  complexityScore?: number;
}

/**
 * Processed variant for UI display
 */
export interface ProcessedVariant extends Variant {
  isHappyPath: boolean;
  hasRework: boolean;
  avgDurationSeconds: number;
  conformanceScore?: number;
}

// ============================================
// Activity Types
// ============================================

/**
 * Activity detail from SDK
 */
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

/**
 * Activity data for UI display
 */
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

/**
 * Edge detail for UI display
 */
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

/**
 * DFG Node data for ProcessCanvas
 */
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

/**
 * DFG Edge data for ProcessCanvas
 */
export interface DFGEdgeData {
  source: string;
  target: string;
  frequency: number;
  performance?: number; // avg duration in seconds
}

/**
 * Metric display mode
 */
export type MetricMode = 'frequency' | 'performance';

// ============================================
// Filter Types
// ============================================

/**
 * Filter type enumeration
 */
export type FilterType =
  | 'timeRange'
  | 'activity'
  | 'activitySequence'
  | 'performance'
  | 'resource'
  | 'variant'
  | 'rework';

/**
 * Applied filter
 */
export interface AppliedFilter {
  id: string;
  type: FilterType;
  label: string;
  value: unknown;
  color?: string;
}

/**
 * Filter options available for the current log
 */
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

/**
 * Process KPIs for the KPI bar
 */
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

/**
 * Options for building DFG
 */
export interface DFGBuildOptions {
  includePerformance?: boolean;
  activityThreshold?: number;
  pathThreshold?: number;
}

/**
 * Options for getting variants
 */
export interface VariantOptions {
  topN?: number;
  includeComplexity?: boolean;
}

// ============================================
// Utility Functions
// ============================================

/**
 * Check if a variant has rework (repeated activities)
 */
export function hasReworkInVariant(activities: string[]): boolean {
  const seen = new Set<string>();
  for (const activity of activities) {
    if (seen.has(activity)) return true;
    seen.add(activity);
  }
  return false;
}

/**
 * Transform SDK variant to processed variant for UI
 */
export function toProcessedVariant(variant: Variant, index: number): ProcessedVariant {
  return {
    ...variant,
    avgDurationSeconds: variant.avgDuration ?? 0,
    isHappyPath: index === 0 && variant.frequencyPercent > 50,
    hasRework: hasReworkInVariant(variant.activities),
  };
}

/**
 * Transform activity detail to activity data for UI
 */
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
