/**
 * Discovery Zod Schemas - DFG, Variants, Activities
 * 
 * FIXED: Standardized on dataset_id (was dataset_id)
 */
import { z } from 'zod';

// ============================================
// DFG (Directly-Follows Graph)
// ============================================

export const DFGNodeResponseSchema = z.object({
  id: z.string(),
  name: z.string(),
  frequency: z.number(),
  is_start: z.boolean(),
  is_end: z.boolean(),
});

export type DFGNodeResponse = z.infer<typeof DFGNodeResponseSchema>;

export const DFGEdgeResponseSchema = z.object({
  source: z.string(),
  target: z.string(),
  frequency: z.number(),
  probability: z.number(),
  avg_duration_seconds: z.number().optional(),
  min_duration_seconds: z.number().optional(),
  max_duration_seconds: z.number().optional(),
});

export type DFGEdgeResponse = z.infer<typeof DFGEdgeResponseSchema>;

export const DFGResponseSchema = z.object({
  nodes: z.array(DFGNodeResponseSchema),
  edges: z.array(DFGEdgeResponseSchema),
  start_activities: z.record(z.string(), z.number()),
  end_activities: z.record(z.string(), z.number()),
  total_frequency: z.number(),
});

export type DFGResponse = z.infer<typeof DFGResponseSchema>;

// ============================================
// Variants
// ============================================

export const VariantResponseSchema = z.object({
  variant_key: z.string(),
  activity_trace: z.string(),
  activities: z.array(z.string()).default([]), // Pre-parsed activities array
  case_count: z.number(),
  frequency_percent: z.number(),
  avg_duration_seconds: z.number().optional(),
  complexity_score: z.number().optional(),
  rework_count: z.number().optional(),
  unique_activity_count: z.number().optional(),
});

export type VariantResponse = z.infer<typeof VariantResponseSchema>;

export const VariantListResponseSchema = z.object({
  variants: z.array(VariantResponseSchema),
  total_variants: z.number(),
  total_cases: z.number(),
});

export type VariantListResponse = z.infer<typeof VariantListResponseSchema>;

// ============================================
// Activities
// ============================================

export const ActivityDetailResponseSchema = z.object({
  activity: z.string(),
  frequency: z.number(),
  frequency_percent: z.number(),
  avg_duration_seconds: z.number().optional(),
  min_duration_seconds: z.number().optional(),
  max_duration_seconds: z.number().optional(),
  is_start_activity: z.boolean(),
  is_end_activity: z.boolean(),
  position_avg: z.number().optional(),
  resources: z.array(z.string()),
});

export type ActivityDetailResponse = z.infer<typeof ActivityDetailResponseSchema>;

export const ActivityListResponseSchema = z.object({
  activities: z.array(ActivityDetailResponseSchema),
  total_activities: z.number(),
});

export type ActivityListResponse = z.infer<typeof ActivityListResponseSchema>;

// ============================================
// Discovery Model
// ============================================

export const DiscoveryModelResponseSchema = z.object({
  model_id: z.string(),
  dataset_id: z.string(), // FIXED: was dataset_id
  miner_type: z.string(),
  model_name: z.string().optional(),
  created_at: z.string(),
});

export type DiscoveryModelResponse = z.infer<typeof DiscoveryModelResponseSchema>;
