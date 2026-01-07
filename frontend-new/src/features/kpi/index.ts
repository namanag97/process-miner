/**
 * KPI Feature Module
 *
 * Self-contained feature module for KPI dashboard.
 * Provides performance analysis, deadline tracking, and automation assessment.
 */

// ============================================
// Page Exports
// ============================================

export { KPIPage } from './pages/KPIPage';

// ============================================
// Hook Exports
// ============================================

export {
  usePerformance,
  useCycleTime,
  useThroughput,
  useProcess,
} from './hooks';

// ============================================
// Component Exports
// ============================================

export {
  PerformanceTab,
  DeadlinesTab,
  UnwantedActivitiesTab,
  AutomationTab,
} from './components';

// ============================================
// Type Exports
// ============================================

export type {
  PerformanceData,
  BottleneckActivity,
  CycleTimeData,
  ThroughputData,
  DeadlineData,
  DeadlineConfig,
  UnwantedActivityData,
  UnwantedActivitiesResponse,
  AutomationPotentialData,
  AutomationResponse,
  KPITabProps,
} from './types';
