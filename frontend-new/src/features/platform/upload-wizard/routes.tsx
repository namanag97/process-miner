/**
 * Upload Wizard Feature Routes
 */

import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

// Lazy load pages
const UploadWizardPage = lazy(() => import('./pages/UploadWizardPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const uploadWizardRouteConfig: RouteObject[] = [
    // Celonis-style 5-step upload wizard
    {
        path: '/workspace/:projectId/upload',
        element: (
            <ErrorBoundary
                fallbackRender={({ error, resetErrorBoundary }) => (
                    <FeatureErrorFallback
                        error={error}
                        resetError={resetErrorBoundary}
                        featureName="Upload Wizard"
                    />
                )}
                onError={(error) => console.error('[UploadWizard] Error:', error)}
            >
                <UploadWizardPage />
            </ErrorBoundary>
        )
    },
];
