/**
 * Projects Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

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
    <Routes>
      <Route index element={<ProjectsListPage />} />
      <Route path=":projectId" element={<ProjectDetailPage />} />
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  );
}
