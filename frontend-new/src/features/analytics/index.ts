/**
 * Analytics Feature Module
 *
 * Self-contained feature module for process analytics.
 * Provides performance, conformance, rework, and resource analysis.
 */

import { FeatureRegistry } from '../../shared/core/plugins/FeatureRegistry';
import { analyticsRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'analytics';

export const FEATURE_CONFIG = {
  id: 'analytics',
  name: 'Analytics',
  version: '1.0.0',
  icon: 'BarChartOutlined',
  navPath: '/analytics',
  navOrder: 5,
};

// Register feature
FeatureRegistry.register({
  ...FEATURE_CONFIG,
  routes: analyticsRouteConfig,
});

// ============================================
// Page Exports
// ============================================

export { AnalyticsPage } from './pages/AnalyticsPage';

// ============================================
// Route Exports
// ============================================

export { AnalyticsRoutes, analyticsRouteConfig } from './routes';

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
