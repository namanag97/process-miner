/**
 * Discovery Feature Routes
 */

import { lazy } from 'react';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const DiscoveryPage = lazy(() => import('./pages/DiscoveryPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const discoveryRouteConfig: RouteObject[] = [
    // Workspace-scoped discovery
    {
        path: '/workspace/:projectId/data/:datasetId/discovery',
        element: <DiscoveryPage />
    },
];
