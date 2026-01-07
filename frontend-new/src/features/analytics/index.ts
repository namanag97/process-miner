/**
 * Analytics Feature Module
 *
 * Self-contained feature module for process analytics.
 * Provides performance, conformance, rework, and resource analysis.
 */

// ============================================
// Page Exports
// ============================================

export { AnalyticsPage } from './pages/AnalyticsPage';

// ============================================
// Hook Exports
// ============================================

export {
  useAnalyticsPerformance,
  useAnalyticsRework,
  useEventLogs,
} from './hooks';

// ============================================
// Component Exports
// ============================================

export {
  PerformanceTab,
  ConformanceTab,
  ReworkTab,
  ResourcesTab,
} from './components';

// ============================================
// Type Exports
// ============================================

export type {
  AnalyticsPerformanceData,
  BottleneckData,
  ConformanceData,
  ConformanceViolation,
  ReworkData,
  ReworkActivity,
  ReworkPattern,
  ResourceData,
  ResourceDetail,
  HandoffData,
  WorkloadEntry,
  AnalyticsTabProps,
} from './types';
