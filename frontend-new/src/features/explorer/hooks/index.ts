/**
 * Explorer Feature Hooks
 *
 * Re-exports SDK hooks for explorer functionality.
 * These provide the standard way to access discovery/exploration data.
 */

// Re-export discovery hooks from SDK
export {
  useExplorerData,
  useDFG,
  useVariants,
  useActivities,
  useDiscoveredModels,
} from '@/src/api/hooks';

// Re-export dataset hooks for explorer
export { useEventLogsList, useDataset } from '@/src/api/hooks';

// Re-export query keys for direct access
export { queryKeys } from '@/src/api/hooks';

// Process Graph Hook for CytoscapeCanvas
export { useProcessGraph } from './useProcessGraph';
