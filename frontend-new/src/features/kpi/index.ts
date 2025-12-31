/**
 * KPI Feature Module
 *
 * Self-contained feature module for KPI dashboard.
 * Provides performance analysis, deadline tracking, and automation assessment.
 */

import { FeatureRegistry } from '../../core/plugins/FeatureRegistry';
import { kpiRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'kpi';

export const FEATURE_CONFIG = {
  id: 'kpi',
  name: 'KPI Dashboard',
  version: '1.0.0',
  icon: 'DashboardOutlined',
  navPath: '/workspace/:projectId/data/:logId/kpi',
  navOrder: 4,
};

// Register feature
FeatureRegistry.register({
  ...FEATURE_CONFIG,
  routes: kpiRouteConfig,
});

// ============================================
// Page Exports
// ============================================

export { KPIPage } from './pages/KPIPage';

// ============================================
// Route Exports
// ============================================

export { KPIRoutes, kpiRouteConfig } from './routes';

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
