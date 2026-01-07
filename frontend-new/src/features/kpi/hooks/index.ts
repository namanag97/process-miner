/**
 * KPI Feature Hooks
 *
 * Re-exports hooks from design-system and adds any KPI-specific hooks.
 */

// Re-export from design-system
export {
  usePerformance,
  useCycleTime,
  useThroughput,
  useProcess,
} from '@/src/shared/design-system';

// Note: Additional KPI-specific hooks can be added here using createQueryHook
// Example:
// export const useDeadlineAnalysis = createQueryHook({...});
// export const useUnwantedActivities = createQueryHook({...});
// export const useAutomationPotential = createQueryHook({...});
