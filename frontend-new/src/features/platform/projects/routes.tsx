/**
 * Projects Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const ProjectsListPage = lazy(() => import('./pages/ProjectsListPage'));
const ProjectDetailPage = lazy(() => import('./pages/ProjectDetailPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const projectsRouteConfig: RouteObject[] = [
  {
    path: '/workspace',
    children: [
      { index: true, element: <ProjectsListPage /> },
      { path: ':projectId', element: <ProjectDetailPage /> },
    ],
  },
];

/**
 * Routes component for standalone rendering
 */
export function ProjectsRoutes() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName="Projects"
        />
      )}
      onError={(error) => console.error('[Projects] Error:', error)}
    >
      <Routes>
        <Route index element={<ProjectsListPage />} />
        <Route path=":projectId" element={<ProjectDetailPage />} />
        <Route path="*" element={<Navigate to="/workspace" replace />} />
      </Routes>
    </ErrorBoundary>
  );
}
