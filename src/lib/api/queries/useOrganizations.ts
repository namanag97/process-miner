/**
 * Organization API Hooks
 * 
 * React Query hooks for organization CRUD operations.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// =============================================================================
// Types
// =============================================================================

export interface Organization {
    id: string;
    name: string;
    slug: string;
    description: string | null;
    created_at: string;
    user_count: number;
    process_count: number;
}

export interface OrganizationCreate {
    name: string;
    description?: string;
}

// =============================================================================
// API Functions
// =============================================================================

async function fetchOrganizations(): Promise<Organization[]> {
    const res = await fetch(`${API_URL}/api/organizations`);
    if (!res.ok) throw new Error('Failed to fetch organizations');
    return res.json();
}

async function fetchOrganization(orgId: string): Promise<Organization> {
    const res = await fetch(`${API_URL}/api/organizations/${orgId}`);
    if (!res.ok) throw new Error('Failed to fetch organization');
    return res.json();
}

async function createOrganization(data: OrganizationCreate): Promise<Organization> {
    const res = await fetch(`${API_URL}/api/organizations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create organization');
    return res.json();
}

async function deleteOrganization(orgId: string): Promise<void> {
    const res = await fetch(`${API_URL}/api/organizations/${orgId}`, {
        method: 'DELETE',
    });
    if (!res.ok) throw new Error('Failed to delete organization');
}

// =============================================================================
// Hooks
// =============================================================================

export function useOrganizations() {
    return useQuery({
        queryKey: ['organizations'],
        queryFn: fetchOrganizations,
    });
}

export function useOrganization(orgId: string | null) {
    return useQuery({
        queryKey: ['organizations', orgId],
        queryFn: () => fetchOrganization(orgId!),
        enabled: !!orgId,
    });
}

export function useCreateOrganization() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: createOrganization,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
    });
}

export function useDeleteOrganization() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: deleteOrganization,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
    });
}
