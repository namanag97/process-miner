/**
 * Explorer Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

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
    <Routes>
      <Route index element={<ExplorerIndexPage />} />
      <Route path=":datasetId/*" element={<ExplorerDetailPage />} />
      <Route path="*" element={<Navigate to="/explorer" replace />} />
    </Routes>
  );
}
