/**
 * Design System Shim
 * 
 * Local replacements for @lumina/design-system exports.
 * This provides minimal implementations to unblock the build.
 */

// ==============================================
// Design Tokens
// ==============================================
// ==============================================
// Toast (using antd message)
// ==============================================
import { message } from 'antd';

// ==============================================
// SDK Context (implements ProcessMiningSdk)
// ==============================================
import React, { createContext, useContext, ReactNode } from 'react';
import apiClient from '../api/client';
import { env } from '../config/env';
import type { ProcessMiningSdk } from './components';

// ==============================================
// Loading/Error State Components (inline)
// ==============================================
import { Spin, Alert, Button, Card, Table } from 'antd';

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
        surface: {
            default: string;
            card: string;
            elevated: string;
        };
        neutral: Record<number | string, string>;
        [key: string]: unknown;
    };
    spacing: Record<string | number, number>;
    borderRadius: Record<string | number, number>;
    fontSize: Record<string | number, number>;
    radius: Record<string | number, number>;
    fontWeight: Record<string | number, number>;
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
        surface: {
            default: '#ffffff',
            card: '#ffffff',
            elevated: '#fafafa',
        },
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
    fontWeight: {
        normal: 400,
        medium: 500,
        semibold: 600,
        bold: 700,
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

export const toast = {
    success: (content: string) => message.success(content),
    error: (content: string) => message.error(content),
    warning: (content: string) => message.warning(content),
    info: (content: string) => message.info(content),
};

// Create SDK implementation that wraps apiClient
const createSDKInstance = (baseUrl: string): ProcessMiningSdk => {
    const sdk: ProcessMiningSdk = {
        baseUrl,

        // Health check method
        checkHealth: async () => {
            try {
                const response = await apiClient.get('/health');
                return response.status === 200;
            } catch {
                return false;
            }
        },

        // Processes module
        processes: {
            list: async (options?: { pageSize?: number }) => {
                const { data } = await apiClient.get('/processes', { params: options });
                return data;
            },
            get: async (id: string) => {
                const { data } = await apiClient.get(`/processes/${id}`);
                return data;
            },
            analyze: async (id: string) => {
                const { data } = await apiClient.post(`/processes/${id}/analyze`);
                return data;
            },
            getProcessSummary: async (id: string) => {
                const { data } = await apiClient.get(`/processes/${id}/summary`);
                return data;
            },
        },

        // Analytics module
        analytics: {
            performance: async (datasetId: string) => {
                const { data } = await apiClient.get(`/analytics/${datasetId}/performance`);
                return data;
            },
            conformance: async (datasetId: string) => {
                const { data } = await apiClient.get(`/analytics/${datasetId}/conformance`);
                return data;
            },
            getProcessSummary: async (datasetId: string) => {
                const { data } = await apiClient.get(`/analytics/${datasetId}/summary`);
                return data;
            },
        },

        // Predictions module
        predictions: {
            list: async (datasetId: string) => {
                const { data } = await apiClient.get(`/predictions/${datasetId}`);
                return data;
            },
            listPredictors: async (datasetId: string) => {
                const { data } = await apiClient.get(`/predictions/${datasetId}/predictors`);
                return data;
            },
            create: async (datasetId: string, config: any) => {
                const { data } = await apiClient.post(`/predictions/${datasetId}`, config);
                return data;
            },
        },

        // Discovery module
        discovery: {
            dfg: async (datasetId: string, options?: any) => {
                const { data } = await apiClient.get(`/discovery/${datasetId}/dfg`, { params: options });
                return data;
            },
            variants: async (datasetId: string, options?: any) => {
                const { data } = await apiClient.get(`/discovery/${datasetId}/variants`, { params: options });
                return data;
            },
        },

        // Conformance module
        conformance: {
            check: async (datasetId: string, modelId: string) => {
                const { data } = await apiClient.post(`/conformance/${datasetId}/check`, { modelId });
                return data;
            },
        },
    };

    return sdk;
};

type SDKContextType = ProcessMiningSdk;

const SDKContext = createContext<SDKContextType | null>(null);

export const useSDK = (): SDKContextType => {
    const context = useContext(SDKContext);
    if (!context) {
        // Fallback for components used outside provider
        return createSDKInstance(env.API_BASE_URL);
    }
    return context;
};

interface SDKProviderProps {
    children: ReactNode;
    baseUrl?: string;
}

export const SDKProvider: React.FC<SDKProviderProps> = ({ children, baseUrl }) => {
    const url = baseUrl || env.API_BASE_URL;
    const value: SDKContextType = createSDKInstance(url);
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
        rework: (datasetId: string) => [...queryKeys.analytics.all, 'rework', datasetId] as const,
    },
    explorer: {
        all: ['explorer'] as const,
        processes: () => [...queryKeys.explorer.all, 'processes'] as const,
        process: (id: string) => [...queryKeys.explorer.all, 'process', id] as const,
        data: (id: string) => [...queryKeys.explorer.all, 'data', id] as const,
    },
    discovery: {
        all: ['discovery'] as const,
        dfg: (id: string) => ['discovery', 'dfg', id] as const,
        variants: (id: string) => ['discovery', 'variants', id] as const,
        activities: (id: string) => ['discovery', 'activities', id] as const,
    },
    kpi: {
        all: ['kpi'] as const,
        performance: () => [...queryKeys.kpi.all, 'performance'] as const,
    },
    projects: {
        all: () => ['projects'] as const,
        list: (_options?: Record<string, unknown>) => ['projects', 'list'] as const,
        detail: (id: string) => ['projects', 'detail', id] as const,
    },
    datasets: {
        all: ['datasets'] as const,
        list: () => [...queryKeys.datasets.all, 'list'] as const,
        detail: (id: string) => [...queryKeys.datasets.all, 'detail', id] as const,
    },
    conformance: {
        all: ['conformance'] as const,
        check: (datasetId: string, modelId?: string) => ['conformance', 'check', datasetId, modelId] as const,
    },
    processes: {
        all: ['processes'] as const,
        list: () => [...queryKeys.processes.all, 'list'] as const,
        detail: (id: string) => [...queryKeys.processes.all, 'detail', id] as const,
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
    cycleTime: {
        avgSeconds: number;
        minSeconds: number;
        maxSeconds: number;
        medianSeconds: number;
        p75Seconds?: number;
        p95Seconds?: number;
    };
    throughput: {
        casesPerDay: number;
        casesPerWeek?: number;
        casesPerMonth?: number;
        totalCases?: number;
    };
    topBottlenecks: Array<{
        activity: string;
        avgWaitingTime: number;
        impactScore: number;
    }>;
}

export interface ReworkData {
    reworkRate: number;
    reworkPercentage: number;
    totalReworkCases: number;
    averageReworkLoops: number;
    reworkActivities: Array<{
        activity: string;
        reworkCount: number;
        percentage: number;
    }>;
}

export interface ProcessSummaryData {
    id: string;
    name: string;
    description?: string;
    caseCount: number;
    eventCount: number;
    throughput: {
        totalCases: number;
        completedCases?: number;
        casesPerDay: number;
        casesPerWeek?: number;
    };
    cycleTime: {
        avgSeconds: number;
        medianSeconds: number;
        minSeconds: number;
        maxSeconds: number;
    };
    bottlenecks: Array<{
        activity: string;
        avgWaitTime: number;
        avgWaitingTimeSeconds: number;
        isBottleneck: boolean;
        severity: 'low' | 'medium' | 'high';
    }>;
    rework: {
        rate: number;
        count: number;
        reworkPercentage: number;
        totalReworkCases: number;
        activities: Array<{
            activity: string;
            count: number;
            reworkCount: number;
            reworkPercentage: number;
        }>;
    };
    patterns: Array<{
        pattern: string[];
        support: number;
        frequency?: number;
    }>;
    [key: string]: unknown;
}


export interface ActivityDetail {
    id?: string;
    name: string;
    frequency: number;
    avgDuration?: number;
    minDuration?: number;
    maxDuration?: number;
    frequencyPercent?: number;
    resources?: string[];
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
export { PageHeader, MetricCard, ProcessQuestion, EmptyState, AppShell, ErrorBoundary } from './components';
export type { ProcessMiningSdk } from './components';

interface LoadingStateProps {
    type?: 'card' | 'inline' | 'page' | 'fullPage' | 'skeleton';
    rows?: number;
    text?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({ type = 'inline', text }) => {
    if (type === 'card' || type === 'skeleton') {
        return React.createElement(Card, { style: { textAlign: 'center', padding: 40 } },
            React.createElement(Spin, { size: 'large' }),
            text ? React.createElement('div', { style: { marginTop: 16 } }, text) : null
        );
    }
    if (type === 'fullPage' || type === 'page') {
        return React.createElement('div', { style: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' } },
            React.createElement(Spin, { size: 'large' }),
            text ? React.createElement('div', { style: { marginTop: 16 } }, text) : null
        );
    }
    return React.createElement(Spin);
};

interface QueryErrorProps {
    error: Error | unknown;
    onRetry?: () => void;
    variant?: 'inline' | 'card' | 'fullPage';
}

export const QueryError: React.FC<QueryErrorProps> = ({ error, onRetry, variant = 'inline' }) => {
    const errorMessage = error instanceof Error ? error.message : 'An error occurred';
    const alertElement = React.createElement(Alert, {
        type: 'error',
        message: 'Error',
        description: errorMessage,
        action: onRetry ? React.createElement(Button, { onClick: onRetry, size: 'small' }, 'Retry') : undefined,
    });

    if (variant === 'card') {
        return React.createElement(Card, { style: { textAlign: 'center', padding: 40 } }, alertElement);
    }
    if (variant === 'fullPage') {
        return React.createElement('div', { style: { padding: 40, maxWidth: 600, margin: '0 auto' } }, alertElement);
    }
    return alertElement;
};

// ==============================================
// Placeholder KPI Hooks (stub implementations)
// ==============================================
// eslint-disable-next-line @typescript-eslint/no-empty-function
const noopRefetch = () => { };

export const useAutomation = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useDeadlines = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useUnwantedActivities = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useKPIPerformance = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

// ==============================================
// Additional KPI Hooks (stub implementations)
// ==============================================
interface PerformanceStubData {
    topBottlenecks?: Array<{ activity: string; avgWaitingTime: number; impactScore: number }>;
    [key: string]: unknown;
}

interface CycleTimeStubData {
    avg_seconds?: number;
    min_seconds?: number;
    median_seconds?: number;
    max_seconds?: number;
    [key: string]: unknown;
}

interface ThroughputStubData {
    total_cases?: number;
    completed_cases?: number;
    cases_per_day?: number;
    [key: string]: unknown;
}

export const usePerformance = (_datasetId: string) => ({
    data: null as PerformanceStubData | null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useCycleTime = (_datasetId: string) => ({
    data: null as CycleTimeStubData | null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useThroughput = (_datasetId: string) => ({
    data: null as ThroughputStubData | null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useProcess = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useRework = (_datasetId: string) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});

export const useAuditLogs = (_dateFilter?: { start?: Date; end?: Date }) => ({
    data: null,
    isLoading: false,
    error: null,
    refetch: noopRefetch,
});


// ==============================================
// Missing Type Exports (DFG, Variant, etc.)
// ==============================================

export interface DFGNode {
    id: string;
    label: string;
    frequency: number;
    isStart?: boolean;
    isEnd?: boolean;
}

export interface DFGEdge {
    source: string;
    target: string;
    frequency: number;
    avgDuration?: number;
}

export interface DFGData {
    nodes: DFGNode[];
    edges: DFGEdge[];
    startActivities?: Record<string, number>;
    endActivities?: Record<string, number>;
}

export interface Variant {
    key: string;
    activities: string[];
    caseCount: number;
    frequencyPercent: number;
    avgDuration: number | null;
}

export interface AuditLogEntry {
    id: string;
    timestamp: string;
    event: string;
    userId?: string;
    details?: Record<string, unknown>;
}

export interface ProcessQuestion {
    id: string;
    question: string;
    answer?: string;
}

// ==============================================
// DataTable Component
// ==============================================

export interface DataTableColumn<T = unknown> {
    key: string;
    title: string;
    dataIndex?: keyof T | string;
    render?: (value: unknown, record: T) => React.ReactNode;
    width?: number | string;
    sorter?: boolean | ((a: T, b: T) => number);
}

interface DataTableProps<T> {
    columns: DataTableColumn<T>[];
    data?: T[];
    dataSource?: T[];
    loading?: boolean;
    searchable?: boolean;
    searchPlaceholder?: string;
    onRowClick?: (record: T) => void;
    onRefresh?: () => void | Promise<void>;
    rowKey?: string | ((record: T) => string);
    pagination?: any;
}

export const DataTable = <T extends Record<string, any>>(props: DataTableProps<T>) => {
    const { data, dataSource, columns, loading, onRowClick, rowKey = 'id', pagination, ...rest } = props;
    const source = data || dataSource || [];

    return React.createElement(Table, {
        ...rest,
        dataSource: source,
        columns: columns as any,
        loading,
        rowKey,
        pagination,
        onRow: onRowClick ? (record: T) => ({
            onClick: () => onRowClick(record),
            style: { cursor: 'pointer' }
        }) : undefined,
    });
};

// ==============================================
// Instrumented Fetch
// ==============================================

export const instrumentedFetch = async <T = unknown>(
    url: string,
    options?: RequestInit
): Promise<T> => {
    const start = performance.now();
    const method = options?.method || 'GET';
    logRequest(method, url, options?.body);
    try {
        const response = await fetch(url, options);
        const duration = Math.round(performance.now() - start);
        if (!response.ok) {
            logError('fetch', `HTTP ${response.status}`, { url });
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json() as T;
        logResponse(method, url, response.status, duration);
        return data;
    } catch (error) {
        logError('fetch', error as Error, { url });
        throw error;
    }
};
