/**
 * KPI Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const KPIPage = lazy(() => import('./pages/KPIPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const kpiRouteConfig: RouteObject[] = [
  {
    path: '/workspace/:projectId/data/:logId/kpi',
    element: <KPIPage />,
  },
];

/**
 * Routes component for standalone rendering
 */
export function KPIRoutes() {
  return (
    <Routes>
      <Route index element={<KPIPage />} />
    </Routes>
  );
}
