/**
 * Upload Wizard Feature Routes
 */

import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const UploadWizardPage = lazy(() => import('./pages/UploadWizardPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const uploadWizardRouteConfig: RouteObject[] = [
    // Celonis-style 5-step upload wizard
    {
        path: '/workspace/:projectId/upload',
        element: <UploadWizardPage />
    },
];
