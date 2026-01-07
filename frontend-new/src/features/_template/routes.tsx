/**
 * {{FEATURE_NAME_PASCAL}} Feature Routes
 *
 * Route configuration for the {{FEATURE_NAME_PASCAL}} feature.
 * Export routes for integration with the main router.
 */

import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages for code splitting
const {{FEATURE_NAME_PASCAL}}ListPage = lazy(() => import('./pages/{{FEATURE_NAME_PASCAL}}ListPage'));
const {{FEATURE_NAME_PASCAL}}DetailPage = lazy(() => import('./pages/{{FEATURE_NAME_PASCAL}}DetailPage'));

/**
 * Route objects for feature registry integration
 */
export const {{FEATURE_NAME}}RouteConfig: RouteObject[] = [
  {
    path: '/{{FEATURE_NAME}}',
    children: [
      { index: true, element: <{{FEATURE_NAME_PASCAL}}ListPage /> },
      { path: ':id', element: <{{FEATURE_NAME_PASCAL}}DetailPage /> },
    ],
  },
];

/**
 * Routes component for standalone rendering
 */
export function {{FEATURE_NAME}}Routes() {
  return (
    <Routes>
      <Route index element={<{{FEATURE_NAME_PASCAL}}ListPage />} />
      <Route path=":id" element={<{{FEATURE_NAME_PASCAL}}DetailPage />} />
      <Route path="*" element={<Navigate to="/{{FEATURE_NAME}}" replace />} />
    </Routes>
  );
}
