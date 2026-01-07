/**
 * Filter Store
 *
 * Manages process mining filter state for the Explorer feature.
 * Supports URL synchronization via useFilterSync hook.
 */

import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import type { AppliedFilter, FilterType } from '../features/explorer/types';

export interface FilterState {
  // State
  filters: AppliedFilter[];

  // Actions
  addFilter: (filter: AppliedFilter) => void;
  removeFilter: (filterId: string) => void;
  updateFilter: (filterId: string, updates: Partial<AppliedFilter>) => void;
  clearFilters: () => void;
  setFilters: (filters: AppliedFilter[]) => void;

  // Utility methods
  hasFilterType: (type: FilterType) => boolean;
  getFiltersByType: (type: FilterType) => AppliedFilter[];
}

export const useFilterStore = create<FilterState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial state
      filters: [],

      // Actions
      addFilter: (filter) =>
        set(
          (state) => ({ filters: [...state.filters, filter] }),
          false,
          'filters/add'
        ),

      removeFilter: (filterId) =>
        set(
          (state) => ({
            filters: state.filters.filter((f) => f.id !== filterId),
          }),
          false,
          'filters/remove'
        ),

      updateFilter: (filterId, updates) =>
        set(
          (state) => ({
            filters: state.filters.map((f) =>
              f.id === filterId ? { ...f, ...updates } : f
            ),
          }),
          false,
          'filters/update'
        ),

      clearFilters: () => set({ filters: [] }, false, 'filters/clear'),

      setFilters: (filters) => set({ filters }, false, 'filters/set'),

      // Utility methods (not actions, just getters)
      hasFilterType: (type) => get().filters.some((f) => f.type === type),

      getFiltersByType: (type) => get().filters.filter((f) => f.type === type),
    })),
    { name: 'FilterStore' }
  )
);

// Selectors for optimized subscriptions
export const selectFilters = (state: FilterState) => state.filters;
export const selectFilterCount = (state: FilterState) => state.filters.length;
export const selectHasFilters = (state: FilterState) => state.filters.length > 0;
