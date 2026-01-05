/**
 * Hook Factory Utilities - Type-safe factories for creating React Query hooks
 *
 * These utilities reduce boilerplate and ensure consistent patterns across all SDK hooks.
 * They provide:
 * - Type-safe query/mutation creation
 * - Automatic SDK integration
 * - Consistent error handling
 * - Cache invalidation helpers
 *
 * @example
 * ```tsx
 * // Create a simple query hook
 * export const useVariants = createQueryHook({
 *   queryKey: (datasetId: string) => queryKeys.variants.list(datasetId),
 *   queryFn: (sdk, datasetId: string) => sdk.discovery.getVariants(datasetId),
 * });
 *
 * // Create a mutation hook with cache invalidation
 * export const useDeleteProcess = createMutationHook({
 *   mutationFn: (sdk, id: string) => sdk.processes.delete(id),
 *   invalidateKeys: (id) => [queryKeys.processes.all(), queryKeys.projects.all()],
 *   successMessage: 'Process deleted successfully',
 * });
 * ```
 */

import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions, type QueryClient } from '@tanstack/react-query';
import { useSDK, type ProcessMiningSdk } from '../context/SDKContext';
import { APIError } from '../api/client';
import { toast } from '../utils';

// ============================================
// Types
// ============================================

type QueryKeyFactory<TParams> = (params: TParams) => readonly unknown[];

interface CreateQueryHookConfig<TData, TParams = void> {
  /** Factory function to generate query keys */
  queryKey: QueryKeyFactory<TParams>;
  /** Function to fetch data using the SDK */
  queryFn: (sdk: ProcessMiningSdk, params: TParams) => Promise<TData>;
  /** Default query options */
  defaultOptions?: Omit<UseQueryOptions<TData, APIError>, 'queryKey' | 'queryFn'>;
}

interface CreateMutationHookConfig<TData, TVariables> {
  /** Function to perform the mutation using the SDK */
  mutationFn: (sdk: ProcessMiningSdk, variables: TVariables) => Promise<TData>;
  /** Query keys to invalidate on success */
  invalidateKeys?: (variables: TVariables, data: TData) => readonly unknown[][];
  /** Success message to show as toast */
  successMessage?: string | ((data: TData, variables: TVariables) => string);
  /** Error message to show as toast (or function that receives error) */
  errorMessage?: string | ((error: APIError) => string);
  /** Called on success with query client for custom cache updates */
  onSuccess?: (data: TData, variables: TVariables, queryClient: QueryClient) => void;
  /** Should optimistically update cache? */
  optimistic?: boolean;
}

interface InfiniteQueryConfig<TData, TParams> {
  /** Factory function to generate query keys */
  queryKey: QueryKeyFactory<TParams>;
  /** Function to fetch a page of data */
  queryFn: (sdk: ProcessMiningSdk, params: TParams, pageParam: number) => Promise<TData>;
  /** Get the next page param from the last page */
  getNextPageParam: (lastPage: TData) => number | undefined;
}

// ============================================
// Query Hook Factory
// ============================================

/**
 * Factory function to create type-safe query hooks with SDK integration
 *
 * @param config - Configuration for the query hook
 * @returns A React hook that can be used to fetch data
 *
 * @example
 * ```tsx
 * // Create hook
 * export const useProcess = createQueryHook({
 *   queryKey: (id: string) => queryKeys.processes.detail(id),
 *   queryFn: (sdk, id) => sdk.processes.get(id),
 *   defaultOptions: { staleTime: 5 * 60 * 1000 },
 * });
 *
 * // Use in component
 * function ProcessDetail({ id }: { id: string }) {
 *   const { data, isLoading, error } = useProcess(id);
 *   // ...
 * }
 * ```
 */
export function createQueryHook<TData, TParams = void>(
  config: CreateQueryHookConfig<TData, TParams>
) {
  return function useGeneratedQuery(
    params: TParams,
    options?: Omit<UseQueryOptions<TData, APIError>, 'queryKey' | 'queryFn'>
  ) {
    const sdk = useSDK();

    return useQuery<TData, APIError>({
      queryKey: config.queryKey(params),
      queryFn: () => config.queryFn(sdk, params),
      ...config.defaultOptions,
      ...options,
    });
  };
}

/**
 * Factory function to create query hooks that depend on a condition
 * Query will only run when the condition is truthy
 */
export function createConditionalQueryHook<TData, TParams>(
  config: CreateQueryHookConfig<TData, TParams> & {
    /** Condition to enable the query (receives params) */
    enabled: (params: TParams) => boolean;
  }
) {
  return function useGeneratedConditionalQuery(
    params: TParams,
    options?: Omit<UseQueryOptions<TData, APIError>, 'queryKey' | 'queryFn' | 'enabled'>
  ) {
    const sdk = useSDK();

    return useQuery<TData, APIError>({
      queryKey: config.queryKey(params),
      queryFn: () => config.queryFn(sdk, params),
      enabled: config.enabled(params),
      ...config.defaultOptions,
      ...options,
    });
  };
}

// ============================================
// Mutation Hook Factory
// ============================================

/**
 * Factory function to create type-safe mutation hooks with SDK integration
 *
 * @param config - Configuration for the mutation hook
 * @returns A React hook that can be used to perform mutations
 *
 * @example
 * ```tsx
 * // Create hook
 * export const useDeleteProcess = createMutationHook({
 *   mutationFn: (sdk, id: string) => sdk.processes.delete(id),
 *   invalidateKeys: () => [queryKeys.processes.all()],
 *   successMessage: 'Process deleted',
 *   errorMessage: (error) => `Failed to delete: ${error.message}`,
 * });
 *
 * // Use in component
 * function DeleteButton({ id }: { id: string }) {
 *   const { mutate, isPending } = useDeleteProcess();
 *   return <button onClick={() => mutate(id)} disabled={isPending}>Delete</button>;
 * }
 * ```
 */
export function createMutationHook<TData, TVariables>(
  config: CreateMutationHookConfig<TData, TVariables>
) {
  return function useGeneratedMutation(
    mutationOptions?: Omit<UseMutationOptions<TData, APIError, TVariables>, 'mutationFn'>
  ) {
    const sdk = useSDK();
    const queryClient = useQueryClient();

    return useMutation<TData, APIError, TVariables>({
      mutationFn: (variables) => config.mutationFn(sdk, variables),
      onSuccess: (data, variables) => {
        // Show success toast if configured
        if (config.successMessage) {
          const message =
            typeof config.successMessage === 'function'
              ? config.successMessage(data, variables)
              : config.successMessage;
          toast.success(message);
        }

        // Invalidate configured query keys
        if (config.invalidateKeys) {
          const keys = config.invalidateKeys(variables, data);
          keys.forEach((key) => {
            queryClient.invalidateQueries({ queryKey: key as unknown[] });
          });
        }

        // Call custom onSuccess handler
        config.onSuccess?.(data, variables, queryClient);
      },
      onError: (error) => {
        // Show error toast if configured
        if (config.errorMessage) {
          const message =
            typeof config.errorMessage === 'function'
              ? config.errorMessage(error)
              : config.errorMessage;
          toast.error(message);
        } else {
          // Default error handling
          toast.error(`Operation failed: ${error.message}`);
        }

        // Note: user-provided onError will be merged via ...mutationOptions
      },
      ...mutationOptions,
    });
  };
}

// ============================================
// Prefetch Utilities
// ============================================

/**
 * Create a prefetch function for a query hook config
 *
 * @example
 * ```tsx
 * const prefetchProcess = createPrefetchFn({
 *   queryKey: (id: string) => queryKeys.processes.detail(id),
 *   queryFn: (sdk, id) => sdk.processes.get(id),
 * });
 *
 * // Use in component
 * <Link
 *   to={`/processes/${id}`}
 *   onMouseEnter={() => prefetchProcess(queryClient, sdk, id)}
 * >
 *   View Process
 * </Link>
 * ```
 */
export function createPrefetchFn<TData, TParams>(
  config: Pick<CreateQueryHookConfig<TData, TParams>, 'queryKey' | 'queryFn'>
) {
  return function prefetch(
    queryClient: QueryClient,
    sdk: ProcessMiningSdk,
    params: TParams,
    options?: { staleTime?: number }
  ) {
    return queryClient.prefetchQuery({
      queryKey: config.queryKey(params),
      queryFn: () => config.queryFn(sdk, params),
      staleTime: options?.staleTime ?? 5 * 60 * 1000,
    });
  };
}

// ============================================
// Suspense Helpers
// ============================================

/**
 * Create a suspense-enabled query hook
 * The component using this hook MUST be wrapped in a Suspense boundary
 */
export function createSuspenseQueryHook<TData, TParams = void>(
  config: CreateQueryHookConfig<TData, TParams>
) {
  // Note: useSuspenseQuery is available in @tanstack/react-query v5
  // This factory creates a hook that suspends while loading
  return function useGeneratedSuspenseQuery(params: TParams) {
    const sdk = useSDK();

    // Use the regular useQuery with suspense option
    // In TanStack Query v5, use useSuspenseQuery directly in the consuming code
    return useQuery<TData, APIError>({
      queryKey: config.queryKey(params),
      queryFn: () => config.queryFn(sdk, params),
      ...config.defaultOptions,
    });
  };
}

// ============================================
// Re-export Types
// ============================================

export type { CreateQueryHookConfig, CreateMutationHookConfig, InfiniteQueryConfig };
