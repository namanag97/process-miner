/**
 * Design System Hooks - Re-exports all query and utility hooks
 */

// Hook Factory Utilities
export {
  createQueryHook,
  createConditionalQueryHook,
  createMutationHook,
  createPrefetchFn,
  createSuspenseQueryHook,
  type CreateQueryHookConfig,
  type CreateMutationHookConfig,
} from './createHookFactory';

// Query Hooks - Projects
export {
  useProjects,
  useProject,
  useCreateProject,
  useUpdateProject,
  useDeleteProject,
  useAddFileToProject,
  useRemoveFileFromProject,
} from './useProjects';

// Query Hooks - Processes
export {
  useProcesses,
  useProcess,
  useProjectProcesses,
  useUploadProcess,
  useDeleteProcess,
  useDetectColumns,
  useProcessStatistics,
} from './useProcesses';

// Query Hooks - Discovery
export {
  useDFG,
  useVariants,
  useActivities,
  useDiscoverProcess,
  useExplorerData,
} from './useDiscovery';

// Query Hooks - Analytics
export {
  usePerformance,
  useRework,
  useBottlenecks,
  useCycleTime,
  useThroughput,
  usePatterns,
  useProcessSummary,
  useDeadlines,
  useAutomation,
  useKPIData,
} from './useAnalytics';

// Query Hooks - Audit
export {
  useAuditLogs,
  useLogAuditEvent,
  type AuditFilters,
  type AuditLogEntry,
  type AuditEventType,
} from './useAudit';
