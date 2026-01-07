/**
 * Organizational Mining Zod Schemas - Networks, Resources, Workload
 */
import { z } from 'zod';

// ============================================
// Social Network
// ============================================

export const NetworkNodeSchema = z.object({
  id: z.string(),
  label: z.string(),
  size: z.number().optional(),
  centrality: z.number().optional(),
});

export type NetworkNode = z.infer<typeof NetworkNodeSchema>;

export const NetworkEdgeSchema = z.object({
  source: z.string(),
  target: z.string(),
  weight: z.number(),
  label: z.string().optional(),
});

export type NetworkEdge = z.infer<typeof NetworkEdgeSchema>;

export const NetworkMetricsSchema = z.object({
  density: z.number(),
  avg_centrality: z.number(),
  num_nodes: z.number().optional(),
  num_edges: z.number().optional(),
});

export type NetworkMetrics = z.infer<typeof NetworkMetricsSchema>;

export const NetworkTypeSchema = z.enum(['handover', 'collaboration', 'similarity']);
export type NetworkType = z.infer<typeof NetworkTypeSchema>;

export const SocialNetworkResponseSchema = z.object({
  dataset_id: z.string(),
  network_type: NetworkTypeSchema,
  nodes: z.array(NetworkNodeSchema),
  edges: z.array(NetworkEdgeSchema),
  metrics: NetworkMetricsSchema,
});

export type SocialNetworkResponse = z.infer<typeof SocialNetworkResponseSchema>;

// ============================================
// Resource Roles
// ============================================

export const ResourceRoleSchema = z.object({
  resource: z.string(),
  role: z.string(),
  activities: z.array(z.string()),
  case_count: z.number(),
  event_count: z.number(),
});

export type ResourceRole = z.infer<typeof ResourceRoleSchema>;

export const ResourceRoleListResponseSchema = z.object({
  roles: z.array(ResourceRoleSchema),
  total_resources: z.number(),
  unique_roles: z.number(),
});

export type ResourceRoleListResponse = z.infer<typeof ResourceRoleListResponseSchema>;

// ============================================
// Resource Profile
// ============================================

export const ActivityPerformanceSchema = z.object({
  activity: z.string(),
  count: z.number(),
  avg_duration_seconds: z.number().optional(),
  percentage: z.number(),
});

export type ActivityPerformance = z.infer<typeof ActivityPerformanceSchema>;

export const ResourceProfileResponseSchema = z.object({
  resource: z.string(),
  total_events: z.number(),
  total_cases: z.number(),
  activities: z.array(ActivityPerformanceSchema),
  avg_events_per_case: z.number(),
  first_event_date: z.string().optional(),
  last_event_date: z.string().optional(),
});

export type ResourceProfileResponse = z.infer<typeof ResourceProfileResponseSchema>;

// ============================================
// Workload Distribution
// ============================================

export const ResourceWorkloadSchema = z.object({
  resource: z.string(),
  event_count: z.number(),
  case_count: z.number(),
  workload_percentage: z.number(),
  avg_events_per_day: z.number().optional(),
});

export type ResourceWorkload = z.infer<typeof ResourceWorkloadSchema>;

export const WorkloadDistributionResponseSchema = z.object({
  dataset_id: z.string(),
  resources: z.array(ResourceWorkloadSchema),
  total_events: z.number(),
  total_resources: z.number(),
  gini_coefficient: z.number().optional(),
});

export type WorkloadDistributionResponse = z.infer<typeof WorkloadDistributionResponseSchema>;
