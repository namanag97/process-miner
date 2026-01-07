/**
 * useExplorerFilters - URL State Management for Explorer Filters
 *
 * This hook manages filter state in the URL, enabling:
 * - Shareable filter configurations via URL
 * - Browser back/forward navigation through filter history
 * - Persistent filters across page refreshes
 *
 * URL Parameters:
 * - filters: Base64-encoded JSON array of AppliedFilter objects
 *
 * @example
 * const { filters, addFilter, removeFilter, clearFilters, isUrlSynced } = useExplorerFilters();
 */

import { useCallback, useMemo, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { createLogger } from '../../../shared/lib/logger';
import type { AppliedFilter, FilterType } from '../types';

const log = createLogger('useExplorerFilters');

const FILTER_PARAM_KEY = 'filters';

/**
 * Serialize filters to a URL-safe string
 */
function serializeFilters(filters: AppliedFilter[]): string {
  if (filters.length === 0) return '';
  try {
    // Use a compact format for URL
    const compactFilters = filters.map(f => ({
      i: f.id,
      t: f.type,
      l: f.label,
      v: f.value,
      c: f.color,
    }));
    return btoa(JSON.stringify(compactFilters));
  } catch (error) {
    log.error('Failed to serialize filters', error);
    return '';
  }
}

/**
 * Deserialize filters from URL string
 */
function deserializeFilters(encoded: string): AppliedFilter[] {
  if (!encoded) return [];
  try {
    const compactFilters = JSON.parse(atob(encoded));
    return compactFilters.map((f: { i: string; t: FilterType; l: string; v: unknown; c?: string }) => ({
      id: f.i,
      type: f.t,
      label: f.l,
      value: f.v,
      color: f.c,
    }));
  } catch (error) {
    log.warn('Failed to deserialize filters from URL', error);
    return [];
  }
}

export interface UseExplorerFiltersOptions {
  /** Whether to sync filters to URL (default: true) */
  syncToUrl?: boolean;
  /** Initial filters if none in URL */
  initialFilters?: AppliedFilter[];
  /** Callback when filters change */
  onFiltersChange?: (filters: AppliedFilter[]) => void;
}

export interface UseExplorerFiltersReturn {
  /** Current applied filters */
  filters: AppliedFilter[];
  /** Add a new filter */
  addFilter: (filter: AppliedFilter) => void;
  /** Remove a filter by ID */
  removeFilter: (filterId: string) => void;
  /** Clear all filters */
  clearFilters: () => void;
  /** Replace all filters */
  setFilters: (filters: AppliedFilter[]) => void;
  /** Whether the current state is synced with URL */
  isUrlSynced: boolean;
  /** Number of active filters */
  filterCount: number;
  /** Check if a specific filter type is active */
  hasFilterType: (type: FilterType) => boolean;
  /** Get filters by type */
  getFiltersByType: (type: FilterType) => AppliedFilter[];
}

export function useExplorerFilters(
  options: UseExplorerFiltersOptions = {}
): UseExplorerFiltersReturn {
  const { syncToUrl = true, initialFilters = [], onFiltersChange } = options;
  const [searchParams, setSearchParams] = useSearchParams();
  const [localFilters, setLocalFilters] = useState<AppliedFilter[]>(initialFilters);
  const [isUrlSynced, setIsUrlSynced] = useState(false);

  // Get filters from URL on mount
  const urlFilters = useMemo(() => {
    if (!syncToUrl) return null;
    const encoded = searchParams.get(FILTER_PARAM_KEY);
    return encoded ? deserializeFilters(encoded) : null;
  }, [searchParams, syncToUrl]);

  // Determine active filters (URL takes precedence if syncing)
  const filters = useMemo(() => {
    if (syncToUrl && urlFilters !== null) {
      return urlFilters;
    }
    return localFilters;
  }, [syncToUrl, urlFilters, localFilters]);

  // Initialize from URL or initial filters
  useEffect(() => {
    if (syncToUrl) {
      const encoded = searchParams.get(FILTER_PARAM_KEY);
      if (encoded) {
        const parsed = deserializeFilters(encoded);
        if (parsed.length > 0) {
          setLocalFilters(parsed);
          setIsUrlSynced(true);
          log.debug('Initialized filters from URL', { count: parsed.length });
        }
      } else if (initialFilters.length > 0) {
        setLocalFilters(initialFilters);
      }
    }
    setIsUrlSynced(true);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Sync filters to URL when they change
  const updateFilters = useCallback(
    (newFilters: AppliedFilter[]) => {
      setLocalFilters(newFilters);

      if (syncToUrl) {
        const serialized = serializeFilters(newFilters);
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
          { replace: true }
        );
      }

      onFiltersChange?.(newFilters);
      log.debug('Filters updated', { count: newFilters.length });
    },
    [syncToUrl, setSearchParams, onFiltersChange]
  );

  const addFilter = useCallback(
    (filter: AppliedFilter) => {
      updateFilters([...filters, filter]);
      log.info('Filter added', { type: filter.type, label: filter.label });
    },
    [filters, updateFilters]
  );

  const removeFilter = useCallback(
    (filterId: string) => {
      const removed = filters.find((f) => f.id === filterId);
      updateFilters(filters.filter((f) => f.id !== filterId));
      if (removed) {
        log.info('Filter removed', { type: removed.type, label: removed.label });
      }
    },
    [filters, updateFilters]
  );

  const clearFilters = useCallback(() => {
    updateFilters([]);
    log.info('All filters cleared');
  }, [updateFilters]);

  const setFilters = useCallback(
    (newFilters: AppliedFilter[]) => {
      updateFilters(newFilters);
    },
    [updateFilters]
  );

  const hasFilterType = useCallback(
    (type: FilterType) => filters.some((f) => f.type === type),
    [filters]
  );

  const getFiltersByType = useCallback(
    (type: FilterType) => filters.filter((f) => f.type === type),
    [filters]
  );

  return {
    filters,
    addFilter,
    removeFilter,
    clearFilters,
    setFilters,
    isUrlSynced,
    filterCount: filters.length,
    hasFilterType,
    getFiltersByType,
  };
}

export default useExplorerFilters;
