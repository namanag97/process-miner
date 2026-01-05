/**
 * Platform Feature Routes
 *
 * Routes for platform layer (settings, projects, uploads, etc.)
 */

import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';

// Import sub-feature routes
import { projectsRouteConfig } from './projects/routes';
import { uploadWizardRouteConfig } from './upload-wizard/routes';

// Lazy load platform pages
const SettingsPage = lazy(() => import('./pages/settings/SettingsPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const ActivityLogPage = lazy(() => import('./pages/ActivityLogPage'));
const AuditLogsPage = lazy(() => import('./pages/AuditLogsPage'));
const HelpCenterPage = lazy(() => import('./pages/HelpCenterPage'));
const TestBenchPage = lazy(() => import('./pages/TestBenchPage'));
const ProcessQuestionsPage = lazy(() => import('./pages/ProcessQuestionsPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const platformRouteConfig: RouteObject[] = [
    // Projects & workspace routes (from projects sub-feature)
    ...projectsRouteConfig,

    // Upload wizard routes (from upload-wizard sub-feature)
    ...uploadWizardRouteConfig,

    // Settings
    { path: '/settings/*', element: <SettingsPage /> },

    // Platform pages
    { path: '/notifications', element: <NotificationsPage /> },
    { path: '/activity', element: <ActivityLogPage /> },
    { path: '/audit-logs', element: <AuditLogsPage /> },
    { path: '/audit', element: <AuditLogsPage /> },
    { path: '/help', element: <HelpCenterPage /> },

    // Developer tools
    { path: '/test-bench', element: <TestBenchPage /> },

    // Questions wizard (workspace-scoped)
    {
        path: '/workspace/:projectId/data/:datasetId/questions',
        element: <ProcessQuestionsPage />
    },
];
