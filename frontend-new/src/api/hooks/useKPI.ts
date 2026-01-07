/**
 * KPI Hooks
 *
 * Additional TanStack Query hooks for KPI/audit operations.
 * Note: useAutomation, useDeadlines, useRework, useUnwantedActivities
 * are exported from useAnalytics.ts
 */

import { useQuery } from '@tanstack/react-query';
import { sdk } from '../sdk';
import { queryKeys } from './queryKeys';

// ============================================
// Audit Hooks
// ============================================

/**
 * Fetch audit logs
 */
export function useAuditLogs(params?: { startDate?: string; endDate?: string }) {
    return useQuery({
        queryKey: queryKeys.audit.logs(params),
        queryFn: () => sdk.audit.list(params),
        staleTime: 1 * 60 * 1000, // 1 minute
    });
}
