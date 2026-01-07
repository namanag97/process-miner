/**
 * SDK Hooks
 *
 * TanStack Query hooks wrapping the Process Mining SDK.
 * These provide the standard way to consume the SDK in React components.
 *
 * @example
 * ```tsx
 * import { useDatasets, useDiscoveryMutation } from '@/api/hooks';
 *
 * function MyComponent() {
 *   const { data, isLoading } = useDatasets();
 *   const discoveryMutation = useDiscoveryMutation();
 *
 *   return <div>...</div>;
 * }
 * ```
 */

export * from './useDatasets';
export * from './useDiscovery';
export * from './useAnalytics';
export * from './useJobs';
export * from './useOperations';  // Unified Temporal operations (v2)
export * from './useProjects';
export * from './useWorkspaces';
export * from './useKPI';

// Re-export query keys for direct access
export { queryKeys } from './queryKeys';
