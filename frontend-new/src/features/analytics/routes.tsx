/**
 * Analytics Feature Routes
 */

import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const analyticsRouteConfig: RouteObject[] = [
  // Standalone analytics routes
  { path: '/analytics', element: <AnalyticsPage /> },
  { path: '/analytics/performance', element: <AnalyticsPage /> },
  { path: '/analytics/conformance', element: <AnalyticsPage /> },
  { path: '/analytics/rework', element: <AnalyticsPage /> },
  { path: '/analytics/resources', element: <AnalyticsPage /> },

  // Workspace-scoped analytics
  { path: '/workspace/:projectId/analytics', element: <AnalyticsPage /> },
  { path: '/workspace/:projectId/analytics/:tab', element: <AnalyticsPage /> },
];

/**
 * Routes component for standalone rendering
 */
export function AnalyticsRoutes() {
  return (
    <Routes>
      <Route index element={<AnalyticsPage />} />
      <Route path="conformance" element={<AnalyticsPage />} />
      <Route path="rework" element={<AnalyticsPage />} />
      <Route path="resources" element={<AnalyticsPage />} />
      <Route path="*" element={<Navigate to="/analytics" replace />} />
    </Routes>
  );
}
