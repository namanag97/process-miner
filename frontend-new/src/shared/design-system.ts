/**
 * Design System Shim
 * 
 * Local replacements for @lumina/design-system exports.
 * This provides minimal implementations to unblock the build.
 */

// ==============================================
// Design Tokens
// ==============================================
export const tokens: {
    colors: {
        primary: string;
        success: string;
        warning: string;
        error: string;
        info: string;
        textPrimary: string;
        textSecondary: string;
        border: string;
        background: string;
        surface: string;
        neutral: Record<number | string, string>;
        [key: string]: unknown;
    };
    spacing: Record<string | number, number>;
    borderRadius: Record<string | number, number>;
    fontSize: Record<string | number, number>;
    radius: Record<string | number, number>;
    [key: string]: unknown;
} = {
    colors: {
        primary: '#1890ff',
        success: '#52c41a',
        warning: '#faad14',
        error: '#ff4d4f',
        info: '#1890ff',
        textPrimary: 'rgba(0, 0, 0, 0.85)',
        textSecondary: 'rgba(0, 0, 0, 0.45)',
        border: '#d9d9d9',
        background: '#f0f2f5',
        surface: '#ffffff',
        neutral: {
            0: '#ffffff',
            50: '#fafafa',
            100: '#f5f5f5',
            200: '#e5e5e5',
            300: '#d4d4d4',
            400: '#a3a3a3',
            500: '#737373',
            600: '#525252',
            700: '#404040',
            800: '#262626',
            900: '#171717',
        },
    },
    spacing: {
        0: 0, 1: 4, 2: 8, 3: 12, 4: 16, 5: 20, 6: 24, 7: 28, 8: 32,
        xs: 4, sm: 8, md: 16, lg: 24, xl: 32,
    },
    borderRadius: {
        0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 6: 12, 8: 16,
        sm: 4, md: 8, lg: 16,
    },
    fontSize: {
        xs: 12, sm: 14, md: 16, lg: 18, xl: 20, '2xl': 24, '3xl': 30,
        0: 12, 1: 14, 2: 16, 3: 18, 4: 20, 5: 24, 6: 30,
    },
    radius: {
        0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 6: 12, 8: 16,
        sm: 4, md: 8, lg: 16,
    },
};

// ==============================================
// Logging Utilities
// ==============================================
export const logAction = (category: string, action?: string | Record<string, unknown>, details?: Record<string, unknown>) => {
    if (typeof action === 'object') {
        console.log(`[Action] ${category}`, action);
    } else {
        console.log(`[Action] ${category}${action ? `: ${action}` : ''}`, details || '');
    }
};

export const logError = (category: string, error?: string | Error | unknown, context?: Record<string, unknown>) => {
    const msg = error instanceof Error ? error.message : String(error || category);
    console.error(`[Error] ${category}: ${msg}`, context || '');
};

export const logRequest = (method: string, url: string, data?: unknown) => {
    console.log(`[Request] ${method} ${url}`, data || '');
};

export const logResponse = (method: string, url: string, status: number, duration?: number | unknown, data?: unknown) => {
    console.log(`[Response] ${method} ${url} - ${status}${typeof duration === 'number' ? ` (${duration}ms)` : ''}`, data || '');
};

// ==============================================
// Toast (using antd message)
// ==============================================
import { message } from 'antd';

export const toast = {
    success: (content: string) => message.success(content),
    error: (content: string) => message.error(content),
    warning: (content: string) => message.warning(content),
    info: (content: string) => message.info(content),
};

// ==============================================
// SDK Context (simplified)
// ==============================================
import React, { createContext, useContext, ReactNode } from 'react';
import apiClient from '../api/client';

interface SDKContextType {
    apiClient: typeof apiClient;
    baseUrl: string;
}

const SDKContext = createContext<SDKContextType | null>(null);

export const useSDK = (): SDKContextType => {
    const context = useContext(SDKContext);
    if (!context) {
        // Fallback for components used outside provider
        return {
            apiClient,
            baseUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
        };
    }
    return context;
};

interface SDKProviderProps {
    children: ReactNode;
    baseUrl?: string;
}

export const SDKProvider: React.FC<SDKProviderProps> = ({ children, baseUrl }) => {
    const value: SDKContextType = {
        apiClient,
        baseUrl: baseUrl || import.meta.env.VITE_API_URL || 'http://localhost:8000',
    };
    return React.createElement(SDKContext.Provider, { value }, children);
};

// ==============================================
// Format Utilities
// ==============================================
export const formatCompactNumber = (num: number): string => {
    if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`;
    if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`;
    return num.toString();
};

export const formatDurationFromSeconds = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
};

// ==============================================
// Query Keys
// ==============================================
export const queryKeys = {
    analytics: {
        all: ['analytics'] as const,
        performance: () => [...queryKeys.analytics.all, 'performance'] as const,
        conformance: () => [...queryKeys.analytics.all, 'conformance'] as const,
        logs: () => [...queryKeys.analytics.all, 'logs'] as const,
    },
    explorer: {
        all: ['explorer'] as const,
        processes: () => [...queryKeys.explorer.all, 'processes'] as const,
        process: (id: string) => [...queryKeys.explorer.all, 'process', id] as const,
    },
    kpi: {
        all: ['kpi'] as const,
        performance: () => [...queryKeys.kpi.all, 'performance'] as const,
    },
    projects: {
        all: ['projects'] as const,
        list: () => [...queryKeys.projects.all, 'list'] as const,
        detail: (id: string) => [...queryKeys.projects.all, 'detail', id] as const,
    },
    datasets: {
        all: ['datasets'] as const,
        list: () => [...queryKeys.datasets.all, 'list'] as const,
        detail: (id: string) => [...queryKeys.datasets.all, 'detail', id] as const,
    },
};

// ==============================================
// Types
// ==============================================
export interface EventLog {
    id: string;
    name: string;
    caseCount: number;
    eventCount: number;
    activityCount: number;
    createdAt: string;
}

export interface PerformanceData {
    averageDuration: number;
    medianDuration: number;
    p95Duration: number;
    totalCases: number;
    cycleTime?: number | { avgSeconds: number };
    [key: string]: unknown;
}

export interface ReworkData {
    reworkRate: number;
    totalReworkCases: number;
    averageReworkLoops: number;
}

export interface ProcessSummaryData {
    id: string;
    name: string;
    description?: string;
    caseCount: number;
    eventCount: number;
    throughput?: number | {
        totalCases?: number;
        completedCases?: number;
        casesPerDay?: number;
        casesPerWeek?: number;
    };
    cycleTime?: number | {
        avgSeconds?: number;
        medianSeconds?: number;
        minSeconds?: number;
        maxSeconds?: number;
    };
    bottlenecks?: Array<{
        activity: string;
        avgWaitTime: number;
        avgWaitingTimeSeconds?: number;
        isBottleneck?: boolean;
        severity?: 'low' | 'medium' | 'high' | string;
    }>;
    rework?: {
        rate: number;
        count: number;
        reworkPercentage?: number;
        totalReworkCases?: number;
        activities?: Array<{ activity: string; count: number }>;
    };
    patterns?: unknown;
    [key: string]: unknown; // Allow additional fields
}


export interface ActivityDetail {
    id?: string;
    name: string;
    frequency: number;
    avgDuration: number;
    [key: string]: unknown;
}

// ==============================================
// Audit Logger Hook
// ==============================================
export const useLogAuditEvent = () => {
    const mutate = (payload: { event: string; data?: Record<string, unknown> }) => {
        logAction(`[Audit] ${payload.event}`, payload.data);
    };
    return { mutate };
};

// ==============================================
// Dev Console Callback
// ==============================================
type LogLevel = 'info' | 'warn' | 'error' | 'debug' | 'action';
type DevConsoleCallback = (level: LogLevel, source: string, message: string, extra?: unknown) => void;

export const registerDevConsoleCallback = (_callback: DevConsoleCallback | null) => {
    // Store callback for dev console integration
    // In production, this would hook into the logging system
};

// ==============================================
// Dev Log (for logger.ts)
// ==============================================
export const devLog = (level: string, namespace: string, message: string, data?: unknown) => {
    const prefix = `[${level}] [${namespace}]`;
    if (level === 'error') {
        console.error(prefix, message, data || '');
    } else if (level === 'warn') {
        console.warn(prefix, message, data || '');
    } else {
        console.log(prefix, message, data || '');
    }
};

// ==============================================
// Placeholder Types for Predictions
// ==============================================
export interface Predictor {
    id: string;
    name: string;
    type: string;
    accuracy?: number;
}

// ==============================================
// Antd Theme
// ==============================================
export const luminaTheme = {
    token: {
        colorPrimary: tokens.colors.primary,
        colorSuccess: tokens.colors.success,
        colorWarning: tokens.colors.warning,
        colorError: tokens.colors.error,
        borderRadius: tokens.borderRadius.md,
    },
};

// ==============================================
// Re-export UI Components
// ==============================================
export { PageHeader, MetricCard, EmptyState, AppShell, ErrorBoundary, ProcessMiningSdk } from './components';

// ==============================================
// Loading/Error State Components (inline)
// ==============================================
import { Spin, Alert, Button, Card } from 'antd';

interface LoadingStateProps {
    type?: 'card' | 'inline' | 'page';
    rows?: number;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ type = 'inline' }) => {
    if (type === 'card') {
        return React.createElement(Card, { style: { textAlign: 'center', padding: 40 } },
            React.createElement(Spin, { size: 'large' })
        );
    }
    return React.createElement(Spin);
};

interface QueryErrorProps {
    error: Error | unknown;
    onRetry?: () => void;
}

export const QueryError: React.FC<QueryErrorProps> = ({ error, onRetry }) => {
    const message = error instanceof Error ? error.message : 'An error occurred';
    return React.createElement(Alert, {
        type: 'error',
        message: 'Error',
        description: message,
        action: onRetry ? React.createElement(Button, { onClick: onRetry, size: 'small' }, 'Retry') : undefined,
    });
};

// ==============================================
// Placeholder KPI Hooks (stub implementations)
// ==============================================
export const useAutomation = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useDeadlines = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useUnwantedActivities = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useKPIPerformance = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

// ==============================================
// Additional KPI Hooks (stub implementations)
// ==============================================
export const usePerformance = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useCycleTime = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useThroughput = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useProcess = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useRework = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

export const useAuditLogs = (_dateFilter?: { start?: Date; end?: Date }) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: () => { },
});

