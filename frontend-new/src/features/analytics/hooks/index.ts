/**
 * Analytics Feature Hooks
 *
 * Re-exports SDK hooks for analytics feature.
 * Provides feature-local aliases for convenience.
 */

// Re-export from SDK hooks
export {
    usePerformance as useAnalyticsPerformance,
    useRework as useAnalyticsRework,
    useBottlenecks,
    useCycleTime,
    useThroughput,
    useAnalyticsDashboard,
    useAutomation,
    useDeadlines,
    useUnwantedActivities,
} from '@/src/api/hooks';

export { useDatasets as useEventLogs } from '@/src/api/hooks';

// Re-export query keys for direct access
export { queryKeys } from '@/src/api/hooks';
