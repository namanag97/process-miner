// Shared Hooks
export { useBackendLogs } from './useBackendLogs';
export { useAuditLogger, useKPIAuditLogger } from './useAuditLogger';
export { useExplorerState } from './useExplorerState';
export { useURLState } from './useURLState';

// Error Handling Hooks
export {
  useQueryWithErrorHandling,
  useQueryWithToast,
  useSilentQuery,
} from './useQueryWithErrorHandling';
export type { UseQueryWithErrorHandlingOptions } from './useQueryWithErrorHandling';

export {
  useSafeAsync,
  useSafeAsyncWithToast,
  useSafeMutation,
} from './useSafeAsync';
export type { UseSafeAsyncOptions, UseSafeAsyncReturn } from './useSafeAsync';

// Network Resilience Hooks
export {
  useNetworkStatus,
  useNetworkInfo,
  useOfflineDuration,
} from './useNetworkStatus';

export {
  useSlowRequestDetection,
  useProgressiveSlowDetection,
} from './useSlowRequestDetection';
export type {
  UseSlowRequestDetectionOptions,
  UseSlowRequestDetectionReturn,
} from './useSlowRequestDetection';
