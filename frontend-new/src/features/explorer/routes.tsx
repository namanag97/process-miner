/**
 * Explorer Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate, type RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const ExplorerIndexPage = lazy(() => import('./pages/ExplorerIndexPage'));
const ExplorerDetailPage = lazy(() => import('./pages/ExplorerDetailPage'));
const ExploreProcessesPage = lazy(() => import('./pages/ExploreProcessesPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const explorerRouteConfig: RouteObject[] = [
  // Standalone explore page
  { path: '/explore', element: <ExploreProcessesPage /> },

  // Explorer index and detail
  { path: '/explorer/:datasetId/*', element: <ExplorerDetailPage /> },

  // Workspace-scoped explorer
  {
    path: '/workspace/:projectId/data/:datasetId/explorer',
    element: <ExplorerDetailPage />
  },
];

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
