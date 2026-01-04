/**
 * Explorer Feature Module
 *
 * Self-contained feature module for process exploration.
 * Provides DFG visualization, variant analysis, and activity inspection.
 */

import { FeatureRegistry } from '../../core/plugins/FeatureRegistry';
import { explorerRouteConfig } from './routes';

// ============================================
// Feature Configuration
// ============================================

export const FEATURE_ID = 'explorer';

export const FEATURE_CONFIG = {
  id: 'explorer',
  name: 'Process Explorer',
  version: '1.0.0',
  icon: 'SearchOutlined',
  navPath: '/explorer',
  navOrder: 3,
};

// Register feature (auto-registration on import)
FeatureRegistry.register({
  ...FEATURE_CONFIG,
  routes: explorerRouteConfig,
});

// ============================================
// Page Exports
// ============================================

export { ExplorerIndexPage } from './pages/ExplorerIndexPage';
export { ExplorerDetailPage } from './pages/ExplorerDetailPage';

// ============================================
// Route Exports
// ============================================

export { ExplorerRoutes, explorerRouteConfig } from './routes';

// ============================================
// Hook Exports
// ============================================

export {
  useDFG,
  useVariants,
  useActivities,
  useLogDetail,
  useEventLogsList,
} from './hooks';

// ============================================
// Component Exports
// ============================================

export { CytoscapeCanvas } from './components/CytoscapeCanvas';
export { ProcessKPIBar } from './components/ProcessKPIBar';
export { VariantPanel } from './components/VariantPanel';
export { ActivityDetailsPanel } from './components/ActivityDetailsPanel';
export { EdgeDetailsPanel } from './components/EdgeDetailsPanel';
export { FilterPanel } from './components/FilterPanel';

// ============================================
// Type Exports
// ============================================

export type {
  DFGNode,
  DFGEdge,
  DFGResponse,
  DFGStats,
  Variant,
  ProcessedVariant,
  ActivityDetail,
  ActivityData,
  EdgeDetail,
  DFGNodeData,
  DFGEdgeData,
  MetricMode,
  FilterType,
  AppliedFilter,
  FilterOptions,
  ProcessKPIs,
  DFGBuildOptions,
  VariantOptions,
} from './types';

export { hasReworkInVariant, toProcessedVariant, toActivityData } from './types';

// ============================================
// Utility Exports
// ============================================

export {
  COLORS,
  getPerformanceColor,
  getFrequencyColor,
  getEdgeStyle,
  getNodeStyle,
  formatDuration,
  formatNumber,
  calculateStats,
} from './utils/colorScales';
