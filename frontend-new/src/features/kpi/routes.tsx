/**
 * KPI Feature Routes
 */

import { lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const KPIPage = lazy(() => import('./pages/KPIPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const kpiRouteConfig: RouteObject[] = [
  {
    path: '/workspace/:projectId/data/:datasetId/kpi',
    element: (
      <ErrorBoundary
        fallbackRender={({ error, resetErrorBoundary }) => (
          <FeatureErrorFallback
            error={error}
            resetError={resetErrorBoundary}
            featureName="KPI Dashboard"
          />
        )}
        onError={(error) => console.error('[KPI] Error:', error)}
      >
        <KPIPage />
      </ErrorBoundary>
    ),
  },
];

/**
 * Routes component for standalone rendering
 */
export function KPIRoutes() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName="KPI Dashboard"
        />
      )}
      onError={(error) => console.error('[KPI] Error:', error)}
    >
      <Routes>
        <Route index element={<KPIPage />} />
      </Routes>
    </ErrorBoundary>
  );
}
