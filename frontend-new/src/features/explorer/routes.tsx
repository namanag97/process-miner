/**
 * Explorer Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const ExplorerIndexPage = lazy(() => import('./pages/ExplorerIndexPage'));
const ExplorerDetailPage = lazy(() => import('./pages/ExplorerDetailPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const explorerRouteConfig: RouteObject[] = [
  {
    path: '/explorer',
    children: [
      { index: true, element: <ExplorerIndexPage /> },
      { path: ':logId', element: <ExplorerDetailPage /> },
    ],
  },
];

/**
 * Routes component for standalone rendering
 */
export function ExplorerRoutes() {
  return (
    <Routes>
      <Route index element={<ExplorerIndexPage />} />
      <Route path=":logId/*" element={<ExplorerDetailPage />} />
      <Route path="*" element={<Navigate to="/explorer" replace />} />
    </Routes>
  );
}
