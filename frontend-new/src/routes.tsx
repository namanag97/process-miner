/**
 * Application Routes
 *
 * Explicit route configuration for the entire application.
 * All routes are defined here in one place for clarity and maintainability.
 *
 * Route structure:
 * - /workspace - Projects and workspace management
 * - /explore - Process exploration
 * - /analytics - Performance analytics
 * - /ai - AI predictions and insights
 * - /settings - User settings
 */

import { lazy, Suspense, type ReactNode } from 'react';
import type { RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';
import { PageLoader } from '@/shared/ui/PageLoader';

// ============================================
// Lazy-loaded Pages
// ============================================

// Note: LandingPage is loaded in App.tsx (rendered outside AppShell)

// Auth
const LoginPage = lazy(() => import('./features/auth/pages/LoginPage'));

// Platform / Workspace
const ProjectsListPage = lazy(() => import('./features/platform/projects/pages/ProjectsListPage'));
const ProjectDetailPage = lazy(() => import('./features/platform/projects/pages/ProjectDetailPage'));
const UploadWizardPage = lazy(() => import('./features/platform/upload-wizard/pages/UploadWizardPage'));
const SettingsPage = lazy(() => import('./features/platform/pages/settings/SettingsPage'));
const NotificationsPage = lazy(() => import('./features/platform/pages/NotificationsPage'));
const ActivityLogPage = lazy(() => import('./features/platform/pages/ActivityLogPage'));
const AuditLogsPage = lazy(() => import('./features/platform/pages/AuditLogsPage'));
const HelpCenterPage = lazy(() => import('./features/platform/pages/HelpCenterPage'));
const TestBenchPage = lazy(() => import('./features/platform/pages/TestBenchPage'));
const ProcessQuestionsPage = lazy(() => import('./features/platform/pages/ProcessQuestionsPage'));

// Explorer
const ExploreProcessesPage = lazy(() => import('./features/explorer/pages/ExploreProcessesPage'));
const ExplorerDetailPage = lazy(() => import('./features/explorer/pages/ExplorerDetailPage'));

// Discovery
const DiscoveryPage = lazy(() => import('./features/discovery/pages/DiscoveryPage'));

// Analytics
const AnalyticsPage = lazy(() => import('./features/analytics/pages/AnalyticsPage'));

// KPI
const KPIPage = lazy(() => import('./features/kpi/pages/KPIPage'));

// AI
const AIIndexPage = lazy(() => import('./features/ai/pages/AIIndexPage'));
const AIAssistantPage = lazy(() => import('./features/ai/pages/AIAssistantPage'));
const AIInsightsPage = lazy(() => import('./features/ai/pages/AIInsightsPage'));
const PredictionsPage = lazy(() => import('./features/ai/pages/PredictionsPage'));
const PredictorDetailPage = lazy(() => import('./features/ai/pages/PredictorDetailPage'));

// ============================================
// Route Helpers
// ============================================

/**
 * Wrap a component with Suspense for lazy loading
 */
function withSuspense(component: ReactNode): ReactNode {
  return (
    <Suspense fallback={<PageLoader fullPage={false} message="Loading..." />}>
      {component}
    </Suspense>
  );
}

/**
 * Wrap a component with error boundary for graceful error handling
 */
function withErrorBoundary(component: ReactNode, featureName: string): ReactNode {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName={featureName}
        />
      )}
      onError={(error) => console.error(`[${featureName}] Error:`, error)}
    >
      {component}
    </ErrorBoundary>
  );
}

/**
 * Wrap a lazy component with both Suspense and ErrorBoundary
 */
function page(component: ReactNode, featureName: string): ReactNode {
  return withSuspense(withErrorBoundary(component, featureName));
}

// ============================================
// Route Configuration
// ============================================

export const routes: RouteObject[] = [
  // Note: Landing page "/" is handled directly in App.tsx via AppRouter
  // to render it outside the AppShell

  // ----------------------------------------
  // Authentication
  // ----------------------------------------
  { path: '/login', element: page(<LoginPage />, 'Login') },

  // ----------------------------------------
  // Workspace & Projects
  // ----------------------------------------
  {
    path: '/workspace',
    children: [
      { index: true, element: page(<ProjectsListPage />, 'Projects') },
      { path: ':projectId', element: page(<ProjectDetailPage />, 'Project') },
    ],
  },

  // ----------------------------------------
  // Upload Wizard
  // ----------------------------------------
  {
    path: '/workspace/:projectId/upload',
    element: page(<UploadWizardPage />, 'Upload Wizard'),
  },

  // ----------------------------------------
  // Dataset-scoped Features
  // ----------------------------------------
  {
    path: '/workspace/:projectId/data/:datasetId/explorer',
    element: page(<ExplorerDetailPage />, 'Process Explorer'),
  },
  {
    path: '/workspace/:projectId/data/:datasetId/discovery',
    element: page(<DiscoveryPage />, 'Process Discovery'),
  },
  {
    path: '/workspace/:projectId/data/:datasetId/kpi',
    element: page(<KPIPage />, 'KPI Dashboard'),
  },
  {
    path: '/workspace/:projectId/data/:datasetId/questions',
    element: page(<ProcessQuestionsPage />, 'Process Questions'),
  },

  // ----------------------------------------
  // Explorer (standalone)
  // ----------------------------------------
  { path: '/explore', element: page(<ExploreProcessesPage />, 'Process Explorer') },
  { path: '/explorer/:datasetId/*', element: page(<ExplorerDetailPage />, 'Process Explorer') },

  // ----------------------------------------
  // Analytics (standalone + workspace-scoped)
  // ----------------------------------------
  { path: '/analytics', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/analytics/performance', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/analytics/conformance', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/analytics/rework', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/analytics/resources', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/workspace/:projectId/analytics', element: page(<AnalyticsPage />, 'Analytics') },
  { path: '/workspace/:projectId/analytics/:tab', element: page(<AnalyticsPage />, 'Analytics') },

  // ----------------------------------------
  // AI & Predictions (standalone + workspace-scoped)
  // ----------------------------------------
  { path: '/ai', element: page(<AIIndexPage />, 'AI & Predictions') },
  { path: '/ai/assistant', element: page(<AIAssistantPage />, 'AI Assistant') },
  { path: '/ai/insights', element: page(<AIInsightsPage />, 'AI Insights') },
  { path: '/ai/predictions', element: page(<PredictionsPage />, 'Predictions') },
  { path: '/ai/predictions/:id', element: page(<PredictorDetailPage />, 'Predictor') },
  { path: '/workspace/:projectId/ai', element: page(<AIIndexPage />, 'AI & Predictions') },
  { path: '/workspace/:projectId/ai/assistant', element: page(<AIAssistantPage />, 'AI Assistant') },
  { path: '/workspace/:projectId/ai/insights', element: page(<AIInsightsPage />, 'AI Insights') },
  { path: '/workspace/:projectId/ai/predictions', element: page(<PredictionsPage />, 'Predictions') },
  { path: '/workspace/:projectId/ai/predictions/:id', element: page(<PredictorDetailPage />, 'Predictor') },

  // ----------------------------------------
  // Platform Pages
  // ----------------------------------------
  { path: '/settings/*', element: page(<SettingsPage />, 'Settings') },
  { path: '/notifications', element: page(<NotificationsPage />, 'Notifications') },
  { path: '/activity', element: page(<ActivityLogPage />, 'Activity Log') },
  { path: '/audit-logs', element: page(<AuditLogsPage />, 'Audit Logs') },
  { path: '/audit', element: page(<AuditLogsPage />, 'Audit Logs') },
  { path: '/help', element: page(<HelpCenterPage />, 'Help Center') },
  { path: '/test-bench', element: page(<TestBenchPage />, 'Test Bench') },
];
