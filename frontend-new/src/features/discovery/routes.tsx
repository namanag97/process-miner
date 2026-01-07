/**
 * Discovery Feature Routes
 */

import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const DiscoveryPage = lazy(() => import('./pages/DiscoveryPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const discoveryRouteConfig: RouteObject[] = [
    // Workspace-scoped discovery
    {
        path: '/workspace/:projectId/data/:datasetId/discovery',
        element: (
            <ErrorBoundary
                fallbackRender={({ error, resetErrorBoundary }) => (
                    <FeatureErrorFallback
                        error={error}
                        resetError={resetErrorBoundary}
                        featureName="Process Discovery"
                    />
                )}
                onError={(error) => console.error('[Discovery] Error:', error)}
            >
                <DiscoveryPage />
            </ErrorBoundary>
        )
    },
];
