/**
 * Route utilities with built-in error handling
 *
 * Provides helper functions to create routes with error boundaries.
 * Uses React Router's errorElement pattern for better error handling.
 */
import type { RouteObject } from 'react-router-dom';
import { FeatureErrorBoundary } from '@/shared/ui';

/**
 * Create a route with error boundary using React Router's errorElement
 *
 * @example
 * ```tsx
 * const routes = [
 *   createRouteWithErrorBoundary({
 *     path: '/explorer/:datasetId',
 *     element: <ExplorerPage />,
 *     featureName: 'Process Explorer',
 *   }),
 * ];
 * ```
 */
export function createRouteWithErrorBoundary(config: {
  path: string;
  element: React.ReactNode;
  featureName: string;
  children?: RouteObject[];
  index?: boolean;
  fallbackPath?: string;
}): RouteObject {
  const { path, element, featureName, children, index, fallbackPath } = config;

  return {
    path,
    element,
    index,
    errorElement: (
      <FeatureErrorBoundary featureName={featureName} fallbackPath={fallbackPath} />
    ),
    children,
  };
}

/**
 * Wrap multiple routes with the same error boundary configuration
 *
 * @example
 * ```tsx
 * const explorerRoutes = wrapRoutesWithErrorBoundary(
 *   [
 *     { path: '/explorer', element: <ExplorerIndex /> },
 *     { path: '/explorer/:id', element: <ExplorerDetail /> },
 *   ],
 *   { featureName: 'Process Explorer' }
 * );
 * ```
 */
export function wrapRoutesWithErrorBoundary(
  routes: RouteObject[],
  config: {
    featureName: string;
    fallbackPath?: string;
  }
): RouteObject[] {
  const { featureName, fallbackPath } = config;
  const errorElement = (
    <FeatureErrorBoundary featureName={featureName} fallbackPath={fallbackPath} />
  );

  return routes.map((route) => ({
    ...route,
    errorElement,
  }));
}

/**
 * Create a parent route that wraps all children with error boundary
 *
 * @example
 * ```tsx
 * const routes = [
 *   createParentRouteWithErrorBoundary({
 *     path: '/explorer',
 *     featureName: 'Process Explorer',
 *     children: [
 *       { index: true, element: <ExplorerIndex /> },
 *       { path: ':id', element: <ExplorerDetail /> },
 *     ],
 *   }),
 * ];
 * ```
 */
export function createParentRouteWithErrorBoundary(config: {
  path: string;
  featureName: string;
  children: RouteObject[];
  element?: React.ReactNode;
  fallbackPath?: string;
}): RouteObject {
  const { path, featureName, children, element, fallbackPath } = config;

  return {
    path,
    element,
    errorElement: (
      <FeatureErrorBoundary featureName={featureName} fallbackPath={fallbackPath} />
    ),
    children,
  };
}
