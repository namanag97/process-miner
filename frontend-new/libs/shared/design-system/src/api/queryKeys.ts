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
    data: (logId: string, options?: DFGOptions) => ['dfg', logId, options] as const,
  },

  variants: {
    list: (logId: string, options?: VariantOptions) => ['variants', logId, options] as const,
  },

  activities: {
    list: (logId: string) => ['activities', logId] as const,
    detail: (logId: string, activityId: string) => ['activities', logId, activityId] as const,
  },

  // ----------------------------------------
  // Explorer (unified data)
  // ----------------------------------------
  explorer: {
    data: (logId: string, options?: { includePerformance?: boolean; topVariants?: number }) =>
      ['explorer', logId, options] as const,
  },

  // ----------------------------------------
  // Analytics
  // ----------------------------------------
  analytics: {
    performance: (logId: string) => ['analytics', 'performance', logId] as const,
    rework: (logId: string) => ['analytics', 'rework', logId] as const,
    bottlenecks: (logId: string) => ['analytics', 'bottlenecks', logId] as const,
    cycleTime: (logId: string) => ['analytics', 'cycleTime', logId] as const,
    throughput: (logId: string) => ['analytics', 'throughput', logId] as const,
    patterns: (logId: string, minSupport?: number) =>
      ['analytics', 'patterns', logId, minSupport] as const,
    summary: (logId: string) => ['analytics', 'summary', logId] as const,
    // KPI page tabs
    deadlines: (logId: string) => ['analytics', 'deadlines', logId] as const,
    automation: (logId: string) => ['analytics', 'automation', logId] as const,
    unwantedActivities: (logId: string) => ['analytics', 'unwantedActivities', logId] as const,
  },

  // ----------------------------------------
  // Conformance
  // ----------------------------------------
  conformance: {
    check: (logId: string, modelId?: string) => ['conformance', logId, modelId] as const,
    diagnostics: (logId: string, modelId?: string) =>
      ['conformance', 'diagnostics', logId, modelId] as const,
  },

  // ----------------------------------------
  // Organizational Mining
  // ----------------------------------------
  organizational: {
    handover: (logId: string) => ['organizational', 'handover', logId] as const,
    collaboration: (logId: string) => ['organizational', 'collaboration', logId] as const,
    similarity: (logId: string) => ['organizational', 'similarity', logId] as const,
    socialNetwork: (logId: string) => ['organizational', 'socialNetwork', logId] as const,
    roles: (logId: string) => ['organizational', 'roles', logId] as const,
    profiles: (logId: string) => ['organizational', 'profiles', logId] as const,
    workload: (logId: string) => ['organizational', 'workload', logId] as const,
    resourceProfile: (logId: string, resource: string) =>
      ['organizational', 'profile', logId, resource] as const,
  },

  // ----------------------------------------
  // Predictions & AI
  // ----------------------------------------
  predictions: {
    all: () => ['predictions'] as const,
    list: (logId?: string) => ['predictions', 'list', logId] as const,
    detail: (predictorId: string) => ['predictions', predictorId] as const,
    results: (predictorId: string, caseId: string) =>
      ['predictions', predictorId, 'results', caseId] as const,
    history: (predictorId: string) => ['predictions', predictorId, 'history'] as const,
  },

  ai: {
    insights: (logId: string) => ['ai', 'insights', logId] as const,
    predictors: () => ['ai', 'predictors'] as const,
    predictor: (id: string) => ['ai', 'predictors', id] as const,
  },

  // ----------------------------------------
  // Simulation
  // ----------------------------------------
  simulation: {
    playOut: (modelId: string) => ['simulation', 'playOut', modelId] as const,
    result: (logId: string) => ['simulation', logId] as const,
    results: (logId: string) => ['simulation', 'results', logId] as const,
    capacity: (logId: string) => ['simulation', 'capacity', logId] as const,
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
  allProcessData: (logId: string) => [
    queryKeys.processes.detail(logId),
    queryKeys.dfg.data(logId),
    queryKeys.variants.list(logId),
    queryKeys.activities.list(logId),
    queryKeys.analytics.summary(logId),
  ],

  /** Invalidate analytics data after re-analysis */
  analyticsData: (logId: string) => [
    queryKeys.analytics.performance(logId),
    queryKeys.analytics.rework(logId),
    queryKeys.analytics.bottlenecks(logId),
    queryKeys.analytics.summary(logId),
  ],

  /** Invalidate project and its processes */
  projectData: (projectId: string) => [
    queryKeys.projects.detail(projectId),
    queryKeys.projects.processes(projectId),
  ],
} as const;
