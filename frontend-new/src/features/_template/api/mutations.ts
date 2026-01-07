/**
 * Feature Mutations (POST/PUT/DELETE requests)
 *
 * Use React Query mutations for all data modifications.
 * Mutations trigger optimistic updates and cache invalidation.
 *
 * @see https://tanstack.com/query/latest/docs/react/guides/mutations
 */

import { useMutation, useQueryClient, type UseMutationOptions } from '@tanstack/react-query';
import { instrumentedFetch, toast } from '@lumina/design-system';
import { FEATURE_ENDPOINTS } from './endpoints';
import { featureQueryKeys } from './queries';
import type {
  CreateFeatureItemRequest,
  UpdateFeatureItemRequest,
  FeatureItem,
} from './types';

/**
 * Create a new feature item
 *
 * @example
 * ```tsx
 * function CreateFeatureForm() {
 *   const createFeature = useCreateFeatureItem();
 *
 *   const handleSubmit = async (data: CreateFeatureItemRequest) => {
 *     try {
 *       const result = await createFeature.mutateAsync(data);
 *       toast.success('Feature created!');
 *       navigate(`/features/${result.id}`);
 *     } catch (error) {
 *       toast.error('Failed to create feature');
 *     }
 *   };
 *
 *   return <form onSubmit={handleSubmit}>...</form>;
 * }
 * ```
 */
export function useCreateFeatureItem(
  options?: UseMutationOptions<FeatureItem, Error, CreateFeatureItemRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CreateFeatureItemRequest) => {
      const response = await instrumentedFetch(FEATURE_ENDPOINTS.create, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(error.message || 'Failed to create feature item');
      }

      return response.json() as Promise<FeatureItem>;
    },
    onSuccess: (data) => {
      // Invalidate list queries to refetch with new item
      queryClient.invalidateQueries({ queryKey: featureQueryKeys.lists() });

      // Optionally: Set detail query data to avoid refetch
      queryClient.setQueryData(featureQueryKeys.detail(data.id), { item: data });

      toast.success('Feature created successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to create feature');
    },
    ...options,
  });
}

/**
 * Update an existing feature item
 *
 * @example
 * ```tsx
 * function EditFeatureForm({ id }: { id: string }) {
 *   const updateFeature = useUpdateFeatureItem();
 *
 *   const handleSave = async (data: UpdateFeatureItemRequest) => {
 *     await updateFeature.mutateAsync({ id, data });
 *   };
 *
 *   return <form onSubmit={handleSave}>...</form>;
 * }
 * ```
 */
export function useUpdateFeatureItem(
  options?: UseMutationOptions<
    FeatureItem,
    Error,
    { id: string; data: UpdateFeatureItemRequest }
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await instrumentedFetch(FEATURE_ENDPOINTS.update(id), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(error.message || 'Failed to update feature item');
      }

      return response.json() as Promise<FeatureItem>;
    },
    onMutate: async ({ id, data }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: featureQueryKeys.detail(id) });

      // Snapshot previous value
      const previousData = queryClient.getQueryData(featureQueryKeys.detail(id));

      // Optimistically update
      if (previousData) {
        queryClient.setQueryData(featureQueryKeys.detail(id), (old: any) => ({
          ...old,
          item: { ...old.item, ...data },
        }));
      }

      return { previousData };
    },
    onError: (error, { id }, context) => {
      // Rollback on error
      if (context?.previousData) {
        queryClient.setQueryData(featureQueryKeys.detail(id), context.previousData);
      }
      toast.error(error.message || 'Failed to update feature');
    },
    onSuccess: (data, { id }) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: featureQueryKeys.detail(id) });
      queryClient.invalidateQueries({ queryKey: featureQueryKeys.lists() });

      toast.success('Feature updated successfully');
    },
    ...options,
  });
}

/**
 * Delete a feature item
 *
 * @example
 * ```tsx
 * function DeleteFeatureButton({ id }: { id: string }) {
 *   const deleteFeature = useDeleteFeatureItem();
 *
 *   const handleDelete = async () => {
 *     if (confirm('Are you sure?')) {
 *       await deleteFeature.mutateAsync(id);
 *       navigate('/features');
 *     }
 *   };
 *
 *   return <Button onClick={handleDelete} danger>Delete</Button>;
 * }
 * ```
 */
export function useDeleteFeatureItem(
  options?: UseMutationOptions<void, Error, string>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const response = await instrumentedFetch(FEATURE_ENDPOINTS.delete(id), {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(error.message || 'Failed to delete feature item');
      }
    },
    onSuccess: (_, id) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: featureQueryKeys.detail(id) });

      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: featureQueryKeys.lists() });

      toast.success('Feature deleted successfully');
    },
    onError: (error) => {
      toast.error(error.message || 'Failed to delete feature');
    },
    ...options,
  });
}

/**
 * Batch operation example
 *
 * Perform an action on multiple items
 */
export function useBatchUpdateFeatureItems(
  options?: UseMutationOptions<void, Error, { ids: string[]; data: Partial<FeatureItem> }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({ ids, data }) => {
      const response = await instrumentedFetch(FEATURE_ENDPOINTS.batchUpdate, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids, data }),
      });

      if (!response.ok) {
        throw new Error('Batch update failed');
      }
    },
    onSuccess: () => {
      // Invalidate all feature queries
      queryClient.invalidateQueries({ queryKey: featureQueryKeys.all });
      toast.success('Batch update completed');
    },
    ...options,
  });
}
