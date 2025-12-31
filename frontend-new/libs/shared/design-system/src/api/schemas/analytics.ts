/**
 * Analytics Zod Schemas - Performance, Rework, Bottlenecks, etc.
 */
import { z } from 'zod';

// ============================================
// Bottlenecks
// ============================================

export const BottleneckResponseSchema = z.object({
  activity: z.string(),
  avg_waiting_time_seconds: z.number(),
  avg_service_time_seconds: z.number(),
  frequency: z.number(),
  is_bottleneck: z.boolean(),
  severity: z.string(),
  preceding_activities: z.array(z.string()),
  following_activities: z.array(z.string()),
  bottleneck_impact_score: z.number(),
});

export type BottleneckResponse = z.infer<typeof BottleneckResponseSchema>;

export const BottleneckListResponseSchema = z.object({
  bottlenecks: z.array(BottleneckResponseSchema),
});

export type BottleneckListResponse = z.infer<typeof BottleneckListResponseSchema>;

// ============================================
// Rework
// ============================================

export const ReworkActivitySchema = z.object({
  activity: z.string(),
  rework_count: z.number(),
  cases_with_rework: z.number(),
  rework_percentage: z.number(),
});

export type ReworkActivity = z.infer<typeof ReworkActivitySchema>;

export const ReworkResponseSchema = z.object({
  log_id: z.string(),
  rework_activities: z.array(ReworkActivitySchema),
  total_rework_cases: z.number(),
  rework_percentage: z.number(),
});

export type ReworkResponse = z.infer<typeof ReworkResponseSchema>;

// ============================================
// Cycle Time
// ============================================

export const CycleTimeResponseSchema = z.object({
  log_id: z.string(),
  min_seconds: z.number(),
  max_seconds: z.number(),
  avg_seconds: z.number(),
  median_seconds: z.number(),
  percentile_25_seconds: z.number(),
  percentile_75_seconds: z.number(),
  percentile_95_seconds: z.number(),
});

export type CycleTimeResponse = z.infer<typeof CycleTimeResponseSchema>;

// ============================================
// Throughput
// ============================================

export const ThroughputResponseSchema = z.object({
  log_id: z.string(),
  total_cases: z.number(),
  completed_cases: z.number(),
  cases_per_day: z.number(),
  cases_per_week: z.number(),
  cases_per_month: z.number(),
  time_range_days: z.number(),
});

export type ThroughputResponse = z.infer<typeof ThroughputResponseSchema>;

// ============================================
// Performance Dashboard
// ============================================

export const PerformanceDashboardResponseSchema = z.object({
  log_id: z.string(),
  cycle_time: CycleTimeResponseSchema,
  throughput: ThroughputResponseSchema,
  top_bottlenecks: z.array(BottleneckResponseSchema),
  rework_summary: z.record(z.string(), z.unknown()),
});

export type PerformanceDashboardResponse = z.infer<typeof PerformanceDashboardResponseSchema>;

// ============================================
// Patterns
// ============================================

export const PatternResponseSchema = z.object({
  pattern: z.array(z.string()),
  support: z.number(),
  confidence: z.number().optional(),
  frequency: z.number(),
});

export type PatternResponse = z.infer<typeof PatternResponseSchema>;

export const PatternListResponseSchema = z.object({
  patterns: z.array(PatternResponseSchema),
  total_patterns: z.number(),
});

export type PatternListResponse = z.infer<typeof PatternListResponseSchema>;

// ============================================
// Process Summary (for AI Assistant)
// ============================================

export const ProcessSummaryResponseSchema = z.object({
  log_id: z.string(),
  name: z.string(),
  total_cases: z.number(),
  total_events: z.number(),
  total_activities: z.number(),
  avg_cycle_time_seconds: z.number().optional(),
  throughput_per_day: z.number().optional(),
  top_bottlenecks: z.array(z.string()).optional(),
  rework_percentage: z.number().optional(),
  most_common_variant: z.string().optional(),
});

export type ProcessSummaryResponse = z.infer<typeof ProcessSummaryResponseSchema>;
