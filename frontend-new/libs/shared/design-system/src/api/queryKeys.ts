/**
 * Query Keys - Centralized constants for TanStack Query cache keys
 *
 * Using a factory pattern ensures type-safe, consistent query keys across the app.
 * All query keys should be defined here to prevent typos and enable refactoring.
 *
 * Usage:
 * ```tsx
 * import { queryKeys } from '@lumina/design-system';
 *
 * useQuery({
 *   queryKey: queryKeys.processes.all(),
 *   queryFn: () => sdk.processes.list(),
 * });
 * ```
 */

// ============================================
// Filter Types (inline to avoid circular deps)
// ============================================

export interface ListProcessesOptions {
  page?: number;
  pageSize?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  search?: string;
}

export interface DFGOptions {
  threshold?: number;
  includePerformance?: boolean;
}

export interface VariantOptions {
  limit?: number;
  minFrequency?: number;
}

export interface AuditFilters {
  userId?: string;
  action?: string;
  startDate?: string;
  endDate?: string;
  page?: number;
  pageSize?: number;
}

// ============================================
// Query Keys Factory
// ============================================

export const queryKeys = {
  // ----------------------------------------
  // Projects
  // ----------------------------------------
  projects: {
    all: () => ['projects'] as const,
    list: (filters?: any) => ['projects', 'list', filters] as const,
    detail: (id: string) => ['projects', id] as const,
    processes: (projectId: string) => ['projects', projectId, 'processes'] as const,
  },

  // ----------------------------------------
  // Processes / Event Logs
  // ----------------------------------------
  processes: {
    all: () => ['processes'] as const,
    list: (filters?: ListProcessesOptions) => ['processes', 'list', filters] as const,
    detail: (id: string) => ['processes', id] as const,
    statistics: (id: string) => ['processes', id, 'statistics'] as const,
    columns: (id: string) => ['processes', id, 'columns'] as const,
  },

  // ----------------------------------------
  // Discovery (DFG, Variants, Activities)
  // ----------------------------------------
  dfg: {
    data: (datasetId: string, options?: DFGOptions) => ['dfg', datasetId, options] as const,
  },

  variants: {
    list: (datasetId: string, options?: VariantOptions) => ['variants', datasetId, options] as const,
  },

  activities: {
    list: (datasetId: string) => ['activities', datasetId] as const,
    detail: (datasetId: string, activityId: string) => ['activities', datasetId, activityId] as const,
  },

  // ----------------------------------------
  // Explorer (unified data)
  // ----------------------------------------
  explorer: {
    data: (datasetId: string, options?: { includePerformance?: boolean; topVariants?: number }) =>
      ['explorer', datasetId, options] as const,
  },

  // ----------------------------------------
  // Analytics
  // ----------------------------------------
  analytics: {
    performance: (datasetId: string) => ['analytics', 'performance', datasetId] as const,
    rework: (datasetId: string) => ['analytics', 'rework', datasetId] as const,
    bottlenecks: (datasetId: string) => ['analytics', 'bottlenecks', datasetId] as const,
    cycleTime: (datasetId: string) => ['analytics', 'cycleTime', datasetId] as const,
    throughput: (datasetId: string) => ['analytics', 'throughput', datasetId] as const,
    patterns: (datasetId: string, minSupport?: number) =>
      ['analytics', 'patterns', datasetId, minSupport] as const,
    summary: (datasetId: string) => ['analytics', 'summary', datasetId] as const,
    // KPI page tabs
    deadlines: (datasetId: string) => ['analytics', 'deadlines', datasetId] as const,
    automation: (datasetId: string) => ['analytics', 'automation', datasetId] as const,
    unwantedActivities: (datasetId: string) => ['analytics', 'unwantedActivities', datasetId] as const,
  },

  // ----------------------------------------
  // Conformance
  // ----------------------------------------
  conformance: {
    check: (datasetId: string, modelId?: string) => ['conformance', datasetId, modelId] as const,
    diagnostics: (datasetId: string, modelId?: string) =>
      ['conformance', 'diagnostics', datasetId, modelId] as const,
  },

  // ----------------------------------------
  // Organizational Mining
  // ----------------------------------------
  organizational: {
    handover: (datasetId: string) => ['organizational', 'handover', datasetId] as const,
    collaboration: (datasetId: string) => ['organizational', 'collaboration', datasetId] as const,
    similarity: (datasetId: string) => ['organizational', 'similarity', datasetId] as const,
    socialNetwork: (datasetId: string) => ['organizational', 'socialNetwork', datasetId] as const,
    roles: (datasetId: string) => ['organizational', 'roles', datasetId] as const,
    profiles: (datasetId: string) => ['organizational', 'profiles', datasetId] as const,
    workload: (datasetId: string) => ['organizational', 'workload', datasetId] as const,
    resourceProfile: (datasetId: string, resource: string) =>
      ['organizational', 'profile', datasetId, resource] as const,
  },

  // ----------------------------------------
  // Predictions & AI
  // ----------------------------------------
  predictions: {
    all: () => ['predictions'] as const,
    list: (datasetId?: string) => ['predictions', 'list', datasetId] as const,
    detail: (predictorId: string) => ['predictions', predictorId] as const,
    results: (predictorId: string, caseId: string) =>
      ['predictions', predictorId, 'results', caseId] as const,
    history: (predictorId: string) => ['predictions', predictorId, 'history'] as const,
  },

  ai: {
    insights: (datasetId: string) => ['ai', 'insights', datasetId] as const,
    predictors: () => ['ai', 'predictors'] as const,
    predictor: (id: string) => ['ai', 'predictors', id] as const,
  },

  // ----------------------------------------
  // Simulation
  // ----------------------------------------
  simulation: {
    playOut: (modelId: string) => ['simulation', 'playOut', modelId] as const,
    result: (datasetId: string) => ['simulation', datasetId] as const,
    results: (datasetId: string) => ['simulation', 'results', datasetId] as const,
    capacity: (datasetId: string) => ['simulation', 'capacity', datasetId] as const,
  },

  // ----------------------------------------
  // Audit Logs
  // ----------------------------------------
  audit: {
    all: () => ['audit'] as const,
    logs: (filters?: AuditFilters) => ['audit', 'logs', filters] as const,
  },

  // ----------------------------------------
  // Notifications
  // ----------------------------------------
  notifications: {
    all: () => ['notifications'] as const,
    list: () => ['notifications', 'list'] as const,
    unreadCount: () => ['notifications', 'unread'] as const,
  },

  // ----------------------------------------
  // Workflows
  // ----------------------------------------
  workflows: {
    all: () => ['workflows'] as const,
    detail: (id: string) => ['workflows', id] as const,
    runs: (workflowId: string) => ['workflows', workflowId, 'runs'] as const,
  },
} as const;

// ============================================
// Type Helpers
// ============================================

/** Type for the queryKeys object */
export type QueryKeys = typeof queryKeys;

/**
 * Extract the query key type for a specific key factory
 * Usage: QueryKeyOf<typeof queryKeys.processes.detail>
 */
export type QueryKeyOf<T extends (...args: never[]) => readonly unknown[]> = ReturnType<T>;

/**
 * All possible query key prefixes for invalidation
 */
export type QueryKeyPrefix =
  | 'projects'
  | 'processes'
  | 'dfg'
  | 'variants'
  | 'activities'
  | 'analytics'
  | 'conformance'
  | 'organizational'
  | 'predictions'
  | 'ai'
  | 'simulation'
  | 'audit'
  | 'notifications'
  | 'workflows';

// ============================================
// Invalidation Helpers
// ============================================

/**
 * Helper to get invalidation key for a domain
 * Useful for invalidating all related queries
 */
export function getInvalidationKey(domain: QueryKeyPrefix): readonly [QueryKeyPrefix] {
  return [domain] as const;
}

/**
 * Common invalidation patterns
 */
export const invalidationKeys = {
  /** Invalidate all process-related data for a log */
  allProcessData: (datasetId: string) => [
    queryKeys.processes.detail(datasetId),
    queryKeys.dfg.data(datasetId),
    queryKeys.variants.list(datasetId),
    queryKeys.activities.list(datasetId),
    queryKeys.analytics.summary(datasetId),
  ],

  /** Invalidate analytics data after re-analysis */
  analyticsData: (datasetId: string) => [
    queryKeys.analytics.performance(datasetId),
    queryKeys.analytics.rework(datasetId),
    queryKeys.analytics.bottlenecks(datasetId),
    queryKeys.analytics.summary(datasetId),
  ],

  /** Invalidate project and its processes */
  projectData: (projectId: string) => [
    queryKeys.projects.detail(projectId),
    queryKeys.projects.processes(projectId),
  ],
} as const;
