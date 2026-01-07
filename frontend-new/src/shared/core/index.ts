/**
 * Core Infrastructure Exports
 *
 * Central export point for core infrastructure used across features.
 * Import from '@/core' (requires path alias setup)
 */

// Hooks
export {
  createQueryHook,
  createMutationHook,
  createOptimisticUpdate,
  createPrefetch,
} from './hooks/createFeatureHook';

// Components
export {
  FeaturePage,
  PageSection,
  type FeaturePageProps,
  type BreadcrumbItem,
  type EmptyStateConfig,
} from './components/FeaturePage';

// Plugin System
export {
  FeatureRegistry,
  useFeatureRegistry,
  useFeatureNavigation,
  useFeatureRoutes,
  type FeatureConfig,
  type NavItem,
} from './plugins/FeatureRegistry';

// Route Utilities
export {
  createRouteWithErrorBoundary,
  wrapRoutesWithErrorBoundary,
  createParentRouteWithErrorBoundary,
} from './utils/createRouteWithErrorBoundary';
