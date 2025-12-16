/**
 * Insights API Hooks
 * 
 * React Query hooks for insights and acknowledgements.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface Insight {
    id: string;
    dataset_id: string;
    insight_type: 'bottleneck' | 'rework' | 'deviation' | 'kpi_alert' | 'recommendation';
    severity: 'low' | 'medium' | 'high' | 'critical';
    severity_score: number;
    title: string;
    description: string;
    affected_activity: string | null;
    affected_case_count: number;
    metric_name: string | null;
    metric_value: number | null;
    is_acknowledged: boolean;
    created_at: string;
}

export interface InsightSummary {
    total_insights: number;
    by_type: Record<string, number>;
    by_severity: Record<string, number>;
    critical_count: number;
    unacknowledged_count: number;
}

// =============================================================================
// API Functions
// =============================================================================

async function fetchInsights(params?: {
    insightType?: string;
    severity?: string;
    acknowledged?: boolean;
    limit?: number;
}): Promise<Insight[]> {
    const searchParams = new URLSearchParams();
    if (params?.insightType) searchParams.set('insight_type', params.insightType);
    if (params?.severity) searchParams.set('severity', params.severity);
    if (params?.acknowledged !== undefined) searchParams.set('acknowledged', String(params.acknowledged));
    if (params?.limit) searchParams.set('limit', String(params.limit));

    const url = `${API_URL}/api/admin/insights?${searchParams}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch insights');
    return res.json();
}

async function fetchInsightSummary(): Promise<InsightSummary> {
    const res = await fetch(`${API_URL}/api/admin/insights/summary`);
    if (!res.ok) throw new Error('Failed to fetch insights summary');
    const data = await res.json();
    return data.summary;
}

async function fetchDatasetInsights(datasetId: string): Promise<Insight[]> {
    // This would require a new endpoint, for now return empty
    return [];
}

async function acknowledgeInsight(insightId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/admin/insights/${insightId}/acknowledge`, {
        method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to acknowledge insight');
}

// =============================================================================
// Hooks
// =============================================================================

export function useInsights(params?: {
    insightType?: string;
    severity?: string;
    acknowledged?: boolean;
    limit?: number;
}) {
    return useQuery({
        queryKey: ['insights', params],
        queryFn: () => fetchInsights(params),
    });
}

export function useInsightSummary() {
    return useQuery({
        queryKey: ['insights', 'summary'],
        queryFn: fetchInsightSummary,
    });
}

export function useDatasetInsights(datasetId: string | null) {
    return useQuery({
        queryKey: ['insights', 'dataset', datasetId],
        queryFn: () => fetchDatasetInsights(datasetId!),
        enabled: !!datasetId,
    });
}

export function useAcknowledgeInsight() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: acknowledgeInsight,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['insights'] });
        },
    });
}

// Helper hook for critical insights
export function useCriticalInsights() {
    return useInsights({ severity: 'critical', acknowledged: false, limit: 10 });
}

// Helper hook for unacknowledged insights
export function useUnacknowledgedInsights(limit = 20) {
    return useInsights({ acknowledged: false, limit });
}
