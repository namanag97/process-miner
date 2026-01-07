/**
 * Explorer Feature Routes
 *
 * Uses React Router's errorElement pattern for graceful error handling.
 * Each route has its own error boundary so errors don't crash the whole app.
 */

import { lazy } from 'react';
import { Routes, Route, Navigate, type RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';
import { wrapRoutesWithErrorBoundary } from '@/shared/core/utils/createRouteWithErrorBoundary';

// Lazy load pages
const ExplorerIndexPage = lazy(() => import('./pages/ExplorerIndexPage'));
const ExplorerDetailPage = lazy(() => import('./pages/ExplorerDetailPage'));
const ExploreProcessesPage = lazy(() => import('./pages/ExploreProcessesPage'));

/**
 * Route configuration for FeatureRegistry
 * Uses React Router's errorElement for route-level error handling
 */
export const explorerRouteConfig: RouteObject[] = wrapRoutesWithErrorBoundary(
  [
    // Standalone explore page
    { path: '/explore', element: <ExploreProcessesPage /> },

    // Explorer index and detail
    { path: '/explorer/:datasetId/*', element: <ExplorerDetailPage /> },

    // Workspace-scoped explorer
    {
      path: '/workspace/:projectId/data/:datasetId/explorer',
      element: <ExplorerDetailPage />,
    },
  ],
  { featureName: 'Process Explorer', fallbackPath: '/workspace' }
);

/**
 * Routes component for standalone rendering
 */
export function ExplorerRoutes() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName="Process Explorer"
        />
      )}
      onError={(error) => console.error('[Explorer] Error:', error)}
    >
      <Routes>
        <Route index element={<ExplorerIndexPage />} />
        <Route path=":datasetId/*" element={<ExplorerDetailPage />} />
        <Route path="*" element={<Navigate to="/explorer" replace />} />
      </Routes>
    </ErrorBoundary>
  );
}
