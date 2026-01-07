/**
 * AI Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route, Navigate, type RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const AIIndexPage = lazy(() => import('./pages/AIIndexPage'));
const AIAssistantPage = lazy(() => import('./pages/AIAssistantPage'));
const AIInsightsPage = lazy(() => import('./pages/AIInsightsPage'));
const PredictionsPage = lazy(() => import('./pages/PredictionsPage'));
const PredictorDetailPage = lazy(() => import('./pages/PredictorDetailPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const aiRouteConfig: RouteObject[] = [
  // Standalone AI routes
  { path: '/ai', element: <AIIndexPage /> },
  { path: '/ai/assistant', element: <AIAssistantPage /> },
  { path: '/ai/insights', element: <AIInsightsPage /> },
  { path: '/ai/predictions', element: <PredictionsPage /> },
  { path: '/ai/predictions/:id', element: <PredictorDetailPage /> },

  // Workspace-scoped AI routes
  { path: '/workspace/:projectId/ai', element: <AIIndexPage /> },
  { path: '/workspace/:projectId/ai/assistant', element: <AIAssistantPage /> },
  { path: '/workspace/:projectId/ai/insights', element: <AIInsightsPage /> },
  { path: '/workspace/:projectId/ai/predictions', element: <PredictionsPage /> },
  { path: '/workspace/:projectId/ai/predictions/:id', element: <PredictorDetailPage /> },
];

/**
 * Routes component for standalone rendering
 */
export function AIRoutes() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName="AI & Predictions"
        />
      )}
      onError={(error) => console.error('[AI] Error:', error)}
    >
      <Routes>
        <Route index element={<AIIndexPage />} />
        <Route path="assistant" element={<AIAssistantPage />} />
        <Route path="insights" element={<AIInsightsPage />} />
        <Route path="predictions" element={<PredictionsPage />} />
        <Route path="predictions/:predictorId" element={<PredictorDetailPage />} />
        <Route path="*" element={<Navigate to="/ai" replace />} />
      </Routes>
    </ErrorBoundary>
  );
}
