/**
 * Discovery Feature - API Hooks
 *
 * Re-exports SDK hooks for discovery operations.
 * Provides feature-local aliases for convenience.
 */

// Re-export from SDK hooks
export {
    useDiscoveryMutation,
    useDiscoveredModels,
    useProcessModel as useModelVisualization,
    useAnalysisMetadata,
    useJobStatus,
    useDFG,
    useVariants,
    useActivities,
    useExplorerData,
} from '@/src/api/hooks';

// Re-export query keys for direct access
export { queryKeys as discoveryQueryKeys } from '@/src/api/hooks';

// Re-export types from SDK
export type {
    DiscoveryRequest,
    DiscoveryResponse,
    Job,
    DFGResponse,
    Variant,
    ProcessModel as DiscoveredModel,
    ExplorerData,
} from '@/src/api/sdk';

// Legacy type alias
export type AnalysisMetadata = {
    miners: Array<{
        id: string;
        name: string;
        description: string;
        parameters: Array<{
            name: string;
            type: string;
            default?: unknown;
            description?: string;
        }>;
    }>;
    analysisTypes: string[];
};
