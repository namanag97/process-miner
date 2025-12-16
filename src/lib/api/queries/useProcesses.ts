/**
 * Process API Hooks
 * 
 * React Query hooks for process CRUD and insights.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface Process {
    id: string;
    org_id: string;
    name: string;
    description: string | null;
    status: 'active' | 'archived' | 'draft';
    icon: string | null;
    color: string | null;
    created_at: string;
    updated_at: string;
    upload_count: number;
    dataset_count: number;
}

export interface ProcessWithStats extends Process {
    total_cases: number;
    total_events: number;
    avg_case_duration_ms: number;
    last_analysis_at: string | null;
}

export interface ProcessCreate {
    name: string;
    description?: string;
    icon?: string;
    color?: string;
}

export interface ProcessUpdate {
    name?: string;
    description?: string;
    status?: string;
    icon?: string;
    color?: string;
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

async function fetchProcesses(orgId?: string): Promise<Process[]> {
    const url = orgId
        ? `${API_URL}/api/processes?org_id=${orgId}`
        : `${API_URL}/api/processes`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch processes');
    return res.json();
}

async function fetchProcess(processId: string): Promise<ProcessWithStats> {
    const res = await fetch(`${API_URL}/api/processes/${processId}`);
    if (!res.ok) throw new Error('Failed to fetch process');
    return res.json();
}

async function createProcess(orgId: string, data: ProcessCreate): Promise<Process> {
    const res = await fetch(`${API_URL}/api/processes?org_id=${orgId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create process');
    return res.json();
}

async function updateProcess(processId: string, data: ProcessUpdate): Promise<Process> {
    const res = await fetch(`${API_URL}/api/processes/${processId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to update process');
    return res.json();
}

async function deleteProcess(processId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/processes/${processId}`, {
        method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete process');
}

async function fetchProcessInsights(processId: string): Promise<InsightSummary> {
    const res = await fetch(`${API_URL}/api/processes/${processId}/insights`);
    if (!res.ok) throw new Error('Failed to fetch process insights');
    return res.json();
}

// =============================================================================
// Hooks
// =============================================================================

export function useProcesses(orgId?: string) {
    return useQuery({
        queryKey: ['processes', orgId],
        queryFn: () => fetchProcesses(orgId),
    });
}

export function useProcess(processId: string | null) {
    return useQuery({
        queryKey: ['processes', processId],
        queryFn: () => fetchProcess(processId!),
        enabled: !!processId,
    });
}

export function useCreateProcess(orgId: string) {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data: ProcessCreate) => createProcess(orgId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['processes'] });
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
    });
}

export function useUpdateProcess() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: ({ processId, data }: { processId: string; data: ProcessUpdate }) =>
            updateProcess(processId, data),
        onSuccess: (_, { processId }) => {
            queryClient.invalidateQueries({ queryKey: ['processes', processId] });
            queryClient.invalidateQueries({ queryKey: ['processes'] });
        },
    });
}

export function useDeleteProcess() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: deleteProcess,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['processes'] });
        },
    });
}

export function useProcessInsights(processId: string | null) {
    return useQuery({
        queryKey: ['processes', processId, 'insights'],
        queryFn: () => fetchProcessInsights(processId!),
        enabled: !!processId,
    });
}
