/**
 * useFilterSync Hook
 *
 * Synchronizes the filterStore with URL search parameters.
 * Enables shareable URLs with filter state.
 *
 * Usage:
 * ```tsx
 * function ExplorerPage() {
 *   useFilterSync(); // Enables URL <-> store sync
 *   const filters = useFilterStore(selectFilters);
 *   // ...
 * }
 * ```
 */

import { useEffect, useRef, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFilterStore, selectFilters } from '../stores/filterStore';
import type { AppliedFilter, FilterType } from '../features/explorer/types';

const FILTER_PARAM_KEY = 'filters';

// Compact format for URL encoding
interface CompactFilter {
  i: string; // id
  t: FilterType; // type
  l: string; // label
  v: unknown; // value
  c?: string; // color
}

/**
 * Serialize filters to URL-safe base64 string
 */
function serializeFilters(filters: AppliedFilter[]): string {
  if (filters.length === 0) return '';
  try {
    const compact: CompactFilter[] = filters.map((f) => ({
      i: f.id,
      t: f.type,
      l: f.label,
      v: f.value,
      c: f.color,
    }));
    return btoa(encodeURIComponent(JSON.stringify(compact)));
  } catch (error) {
    console.warn('[useFilterSync] Failed to serialize filters:', error);
    return '';
  }
}

/**
 * Deserialize filters from URL string
 */
function deserializeFilters(encoded: string): AppliedFilter[] {
  if (!encoded) return [];
  try {
    const json = decodeURIComponent(atob(encoded));
    const compact: CompactFilter[] = JSON.parse(json);
    return compact.map((f) => ({
      id: f.i,
      type: f.t,
      label: f.l,
      value: f.v,
      color: f.c,
    }));
  } catch (error) {
    console.warn('[useFilterSync] Failed to deserialize filters:', error);
    return [];
  }
}

export interface UseFilterSyncOptions {
  /** Enable URL sync (default: true) */
  enabled?: boolean;
  /** Replace history instead of push (default: true) */
  replace?: boolean;
  /** Debounce delay in ms for URL updates (default: 300) */
  debounceMs?: number;
}

export interface UseFilterSyncResult {
  /** Whether initial sync from URL is complete */
  isInitialized: boolean;
  /** Manually trigger sync from URL to store */
  syncFromUrl: () => void;
  /** Manually trigger sync from store to URL */
  syncToUrl: () => void;
  /** Clear filters and URL params */
  clearFiltersAndUrl: () => void;
}

/**
 * Hook to sync filterStore with URL params
 */
export function useFilterSync(
  options: UseFilterSyncOptions = {}
): UseFilterSyncResult {
  const { enabled = true, replace = true, debounceMs = 300 } = options;

  const [searchParams, setSearchParams] = useSearchParams();
  const isInitialized = useRef(false);
  const debounceTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const skipNextUrlUpdate = useRef(false);

  // Get store state and actions
  const filters = useFilterStore(selectFilters);
  const setFilters = useFilterStore((s) => s.setFilters);
  const clearFilters = useFilterStore((s) => s.clearFilters);

  // Sync from URL to store
  const syncFromUrl = useCallback(() => {
    const urlFilters = searchParams.get(FILTER_PARAM_KEY);
    if (urlFilters) {
      const parsed = deserializeFilters(urlFilters);
      if (parsed.length > 0) {
        skipNextUrlUpdate.current = true;
        setFilters(parsed);
      }
    }
  }, [searchParams, setFilters]);

  // Sync from store to URL (debounced)
  const syncToUrl = useCallback(() => {
    if (debounceTimeout.current) {
      clearTimeout(debounceTimeout.current);
    }

    debounceTimeout.current = setTimeout(() => {
      const serialized = serializeFilters(filters);

      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (serialized) {
            next.set(FILTER_PARAM_KEY, serialized);
          } else {
            next.delete(FILTER_PARAM_KEY);
          }
          return next;
        },
        { replace }
      );
    }, debounceMs);
  }, [filters, setSearchParams, replace, debounceMs]);

  // Clear filters and URL
  const clearFiltersAndUrl = useCallback(() => {
    clearFilters();
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete(FILTER_PARAM_KEY);
        return next;
      },
      { replace: true }
    );
  }, [clearFilters, setSearchParams]);

  // Initialize from URL on mount
  useEffect(() => {
    if (!enabled || isInitialized.current) return;

    syncFromUrl();
    isInitialized.current = true;
  }, [enabled, syncFromUrl]);

  // Sync store changes to URL
  useEffect(() => {
    if (!enabled || !isInitialized.current) return;

    // Skip if this update was triggered by URL sync
    if (skipNextUrlUpdate.current) {
      skipNextUrlUpdate.current = false;
      return;
    }

    syncToUrl();

    // Cleanup timeout on unmount
    return () => {
      if (debounceTimeout.current) {
        clearTimeout(debounceTimeout.current);
      }
    };
  }, [enabled, filters, syncToUrl]);

  return {
    isInitialized: isInitialized.current,
    syncFromUrl,
    syncToUrl,
    clearFiltersAndUrl,
  };
}

/**
 * Hook to get filter state from URL without syncing to store
 * Useful for components that just need to read URL filters
 */
export function useUrlFilters(): AppliedFilter[] {
  const [searchParams] = useSearchParams();
  const urlFilters = searchParams.get(FILTER_PARAM_KEY);
  return urlFilters ? deserializeFilters(urlFilters) : [];
}

/**
 * Generate a shareable URL with current filters
 */
export function generateShareableUrl(filters: AppliedFilter[]): string {
  const serialized = serializeFilters(filters);
  const url = new URL(window.location.href);
  if (serialized) {
    url.searchParams.set(FILTER_PARAM_KEY, serialized);
  } else {
    url.searchParams.delete(FILTER_PARAM_KEY);
  }
  return url.toString();
}
