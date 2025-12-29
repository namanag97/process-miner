/**
 * Variant Hooks - React Query hooks for process variant analysis
 */
import { useQuery } from '@tanstack/react-query';
import { useSDK } from '../../../../apps/lumina/src/context/SDKContext';
import type { ProcessVariant } from 'process-mining-sdk';

// Query key factory for variants
export const variantKeys = {
  all: ['variants'] as const,
  list: (logId: string) => ['variants', 'list', logId] as const,
  details: (logId: string, vKey: string) =>
    ['variants', 'details', logId, vKey] as const,
  comparison: (logId: string, keys: string[]) =>
    ['variants', 'comparison', logId, ...keys] as const,
};

/**
 * Get all variants for a log
 */
export function useVariants(logId: string, limit = 100) {
  const sdk = useSDK();

  return useQuery({
    queryKey: variantKeys.list(logId),
    queryFn: () => sdk.logs.listVariants(logId, limit),
    enabled: !!logId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    select: (data) => {
      // Sort by case count descending (most frequent first)
      const variants = [...(data.variants || [])] as ProcessVariant[];
      variants.sort((a: ProcessVariant, b: ProcessVariant) => b.caseCount - a.caseCount);
      return {
        ...data,
        variants,
        totalVariants: variants.length,
        happyPathVariants: variants.filter((v: ProcessVariant) => v.isHappyPath),
      };
    },
  });
}

/**
 * Get details for a specific variant
 */
export function useVariantDetails(logId: string, variantKey: string) {
  const sdk = useSDK();

  return useQuery({
    queryKey: variantKeys.details(logId, variantKey),
    queryFn: async () => {
      // Get all variants and find the specific one
      const response = await sdk.logs.listVariants(logId, 500);
      const variant = response.variants?.find((v: ProcessVariant) => v.key === variantKey);
      if (!variant) {
        throw new Error(`Variant ${variantKey} not found`);
      }
      return variant;
    },
    enabled: !!logId && !!variantKey,
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Compare multiple variants
 */
export function useVariantComparison(logId: string, variantKeysToCompare: string[]) {
  const sdk = useSDK();

  return useQuery({
    queryKey: variantKeys.comparison(logId, variantKeysToCompare),
    queryFn: async () => {
      const response = await sdk.logs.listVariants(logId, 500);
      const selectedVariants = (response.variants?.filter((v: ProcessVariant) =>
        variantKeysToCompare.includes(v.key)
      ) || []) as ProcessVariant[];

      // Calculate comparison metrics
      const totalCases = selectedVariants.reduce((sum: number, v: ProcessVariant) => sum + v.caseCount, 0);
      const avgDuration =
        selectedVariants.reduce((sum: number, v: ProcessVariant) => sum + (v.avgDurationSeconds || 0), 0) /
        selectedVariants.length;

      // Find common and unique activities
      const allActivities = selectedVariants.map((v: ProcessVariant) => new Set(v.activities));
      const commonActivities =
        allActivities.length > 0
          ? [...allActivities[0]].filter((activity: string) =>
              allActivities.every((set: Set<string>) => set.has(activity))
            )
          : [];

      const uniqueActivitiesPerVariant = selectedVariants.map((variant: ProcessVariant) => ({
        variantKey: variant.key,
        uniqueActivities: variant.activities.filter(
          (activity: string) => !commonActivities.includes(activity)
        ),
      }));

      return {
        variants: selectedVariants,
        comparison: {
          totalCases,
          avgDuration,
          commonActivities,
          uniqueActivitiesPerVariant,
          longestVariant: selectedVariants.reduce(
            (max: ProcessVariant, v: ProcessVariant) => (v.activities.length > max.activities.length ? v : max),
            selectedVariants[0]
          ),
          shortestVariant: selectedVariants.reduce(
            (min: ProcessVariant, v: ProcessVariant) => (v.activities.length < min.activities.length ? v : min),
            selectedVariants[0]
          ),
        },
      };
    },
    enabled: !!logId && variantKeysToCompare.length > 0,
    staleTime: 5 * 60 * 1000,
  });
}
