/**
 * Shared Hooks
 *
 * Central export point for all shared hooks.
 */

// Polling hooks
export {
  useAdaptivePolling,
  type AdaptivePollingOptions,
  type AdaptivePollingResult,
} from './useAdaptivePolling';

export {
  useJobStatus,
  useOperationStatus,
  type UseJobStatusOptions,
  type UseJobStatusResult,
  type OperationStatus,
  type UseOperationStatusOptions,
} from './useJobStatus';

export {
  useActiveJobsStatus,
  useJobFromBatch,
  type UseActiveJobsStatusOptions,
  type UseActiveJobsStatusResult,
} from './useActiveJobsStatus';

// URL state hooks
export { useFilterSync } from './useFilterSync';
