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
  {
    path: '/analytics',
    element: <AnalyticsPage />,
    children: [
      { index: true, element: null },
      { path: 'conformance', element: null },
      { path: 'rework', element: null },
      { path: 'resources', element: null },
    ],
  },
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
