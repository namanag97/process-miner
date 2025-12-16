'use client';

import { usePathname } from 'next/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('navigation-guard');

export interface NavigationGuardResult {
    canAccess: boolean;
    redirectPath: string | null;
    toastMessage: string | null;
}

export interface RouteConfig {
    path: string;
    requiresParsedData?: boolean;
    requiresColumnConfig?: boolean;
    requiresMiningResults?: boolean;
}

const routeConfigs: RouteConfig[] = [
    { path: '/', requiresParsedData: false, requiresColumnConfig: false, requiresMiningResults: false },
    { path: '/upload', requiresParsedData: false, requiresColumnConfig: false, requiresMiningResults: false },
    { path: '/configure', requiresParsedData: true, requiresColumnConfig: false, requiresMiningResults: false },
    { path: '/process-map', requiresParsedData: true, requiresColumnConfig: true, requiresMiningResults: false },
    { path: '/insights', requiresParsedData: true, requiresColumnConfig: true, requiresMiningResults: true },
];

export function useNavigationGuard(): NavigationGuardResult {
    const pathname = usePathname();
    const { parsedData, columnConfig, miningResults, sessionId, uploadId } = useAppStore();

    const currentRoute = routeConfigs.find((r) => pathname === r.path || pathname.startsWith(r.path + '/'));

    if (!currentRoute) {
        return { canAccess: true, redirectPath: null, toastMessage: null };
    }

    // Log navigation check
    logger.info('Checking access', {
        pathname,
        sessionId: sessionId?.slice(0, 12),
        uploadId: uploadId?.slice(0, 8),
        hasParsedData: !!parsedData,
        hasColumnConfig: !!columnConfig,
        hasMiningResults: !!miningResults,
        requires: {
            parsedData: currentRoute.requiresParsedData,
            columnConfig: currentRoute.requiresColumnConfig,
            miningResults: currentRoute.requiresMiningResults,
        },
    });

    // Check if requires parsed data
    if (currentRoute.requiresParsedData && !parsedData) {
        logger.warn('Access denied - missing parsedData', { pathname, redirectTo: '/upload' });
        return {
            canAccess: false,
            redirectPath: '/upload',
            toastMessage: 'Please upload a file first',
        };
    }

    // Check if requires column config
    if (currentRoute.requiresColumnConfig && !columnConfig) {
        logger.warn('Access denied - missing columnConfig', { pathname, redirectTo: '/configure' });
        return {
            canAccess: false,
            redirectPath: '/configure',
            toastMessage: 'Please configure your columns first',
        };
    }

    // Check if requires mining results
    if (currentRoute.requiresMiningResults && !miningResults) {
        logger.warn('Access denied - missing miningResults', { pathname, redirectTo: '/process-map' });
        return {
            canAccess: false,
            redirectPath: '/process-map',
            toastMessage: 'Please run analysis first',
        };
    }

    logger.info('Access granted', { pathname });
    return { canAccess: true, redirectPath: null, toastMessage: null };
}

export function getRouteAccessibility(appState: {
    parsedData: unknown;
    columnConfig: unknown;
    miningResults: unknown;
}) {
    return {
        '/': true,
        '/upload': true,
        '/configure': !!appState.parsedData,
        '/process-map': !!appState.parsedData && !!appState.columnConfig,
        '/insights': !!appState.parsedData && !!appState.columnConfig && !!appState.miningResults,
    };
}

export function getCompletedSteps(appState: {
    parsedData: unknown;
    columnConfig: unknown;
    miningResults: unknown;
}) {
    return {
        upload: !!appState.parsedData,
        configure: !!appState.columnConfig,
        'process-map': !!appState.miningResults,
        insights: false, // Last step, never "completed"
    };
}
