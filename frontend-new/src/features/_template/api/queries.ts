/**
 * Feature Queries (GET requests)
 *
 * Use React Query (TanStack Query) for all data fetching.
 * Queries automatically cache, dedupe, and refetch data.
 *
 * @see https://tanstack.com/query/latest/docs/react/guides/queries
 */

import { useQuery, type UseQueryOptions } from '@tanstack/react-query';
import { instrumentedFetch } from '@lumina/design-system';
import { FEATURE_ENDPOINTS } from './endpoints';
import type { FeatureItem, FeatureListResponse, FeatureDetailResponse } from './types';

/**
 * Query keys for this feature
 *
 * Hierarchical structure enables targeted invalidation:
 * - ['feature'] - invalidates all feature queries
 * - ['feature', 'list'] - invalidates all lists
 * - ['feature', 'detail', id] - invalidates specific item
 */
export const featureQueryKeys = {
  all: ['feature'] as const,
  lists: () => [...featureQueryKeys.all, 'list'] as const,
  list: (filters?: Record<string, unknown>) =>
    [...featureQueryKeys.lists(), filters] as const,
  details: () => [...featureQueryKeys.all, 'detail'] as const,
  detail: (id: string) => [...featureQueryKeys.details(), id] as const,
};

/**
 * Fetch list of feature items
 *
 * @example
 * ```tsx
 * function FeatureList() {
 *   const { data, isLoading, error } = useGetFeatureItems({ status: 'active' });
 *
 *   if (isLoading) return <LoadingState type="table" />;
 *   if (error) return <QueryError error={error} />;
 *
 *   return <DataTable data={data.items} />;
 * }
 * ```
 */
export function useGetFeatureItems(
  filters?: { status?: string; limit?: number },
  options?: Omit<UseQueryOptions<FeatureListResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: featureQueryKeys.list(filters),
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters?.status) params.append('status', filters.status);
      if (filters?.limit) params.append('limit', filters.limit.toString());

      const url = `${FEATURE_ENDPOINTS.list}?${params.toString()}`;
      const response = await instrumentedFetch(url);

      if (!response.ok) {
        throw new Error(`Failed to fetch feature items: ${response.statusText}`);
      }

      return response.json() as Promise<FeatureListResponse>;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    ...options,
  });
}

/**
 * Fetch single feature item by ID
 *
 * @example
 * ```tsx
 * function FeatureDetail({ id }: { id: string }) {
 *   const { data, isLoading } = useGetFeatureItem(id);
 *
 *   if (isLoading) return <DetailLoadingState />;
 *
 *   return <FeatureCard item={data.item} />;
 * }
 * ```
 */
export function useGetFeatureItem(
  id: string | null,
  options?: Omit<UseQueryOptions<FeatureDetailResponse>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: featureQueryKeys.detail(id || ''),
    queryFn: async () => {
      const response = await instrumentedFetch(FEATURE_ENDPOINTS.detail(id!));

      if (!response.ok) {
        throw new Error(`Failed to fetch feature item: ${response.statusText}`);
      }

      return response.json() as Promise<FeatureDetailResponse>;
    },
    enabled: !!id, // Only fetch when ID is provided
    staleTime: 5 * 60 * 1000,
    ...options,
  });
}

/**
 * Fetch related items for a feature
 *
 * Example of a nested/related resource query
 */
export function useGetFeatureRelatedItems(
  featureId: string | null,
  options?: Omit<UseQueryOptions<FeatureItem[]>, 'queryKey' | 'queryFn'>
) {
  return useQuery({
    queryKey: [...featureQueryKeys.detail(featureId || ''), 'related'] as const,
    queryFn: async () => {
      const response = await instrumentedFetch(
        FEATURE_ENDPOINTS.related(featureId!)
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch related items: ${response.statusText}`);
      }

      return response.json() as Promise<FeatureItem[]>;
    },
    enabled: !!featureId,
    staleTime: 5 * 60 * 1000,
    ...options,
  });
}
