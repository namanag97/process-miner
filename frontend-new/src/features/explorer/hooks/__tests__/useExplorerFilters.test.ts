/**
 * useExplorerFilters Hook Tests
 *
 * Tests for the URL state management hook for Explorer filters.
 */

import { renderHook, act } from '@testing-library/react';
import { MemoryRouter, useSearchParams } from 'react-router-dom';
import type { ReactNode } from 'react';
import { useExplorerFilters } from '../useExplorerFilters';
import type { AppliedFilter } from '../../types';

// Wrapper with MemoryRouter for testing
function createWrapper(initialPath = '/') {
  return function Wrapper({ children }: { children: ReactNode }) {
    return <MemoryRouter initialEntries={[initialPath]}>{children}</MemoryRouter>;
  };
}

describe('useExplorerFilters', () => {
  describe('initialization', () => {
    it('initializes with empty filters by default', () => {
      const { result } = renderHook(() => useExplorerFilters(), {
        wrapper: createWrapper(),
      });

      expect(result.current.filters).toEqual([]);
      expect(result.current.filterCount).toBe(0);
    });

    it('accepts initial filters', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'test-1', type: 'activity', label: 'Test Filter', value: { activities: ['A'] } },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      expect(result.current.filters).toHaveLength(1);
      expect(result.current.filters[0].id).toBe('test-1');
    });
  });

  describe('addFilter', () => {
    it('adds a filter to the list', () => {
      const { result } = renderHook(() => useExplorerFilters({ syncToUrl: false }), {
        wrapper: createWrapper(),
      });

      const newFilter: AppliedFilter = {
        id: 'filter-1',
        type: 'activity',
        label: 'With: Activity A',
        value: { mode: 'include', activities: ['Activity A'] },
      };

      act(() => {
        result.current.addFilter(newFilter);
      });

      expect(result.current.filters).toHaveLength(1);
      expect(result.current.filters[0].id).toBe('filter-1');
      expect(result.current.filterCount).toBe(1);
    });

    it('allows multiple filters', () => {
      const { result } = renderHook(() => useExplorerFilters({ syncToUrl: false }), {
        wrapper: createWrapper(),
      });

      const filter1: AppliedFilter = {
        id: 'filter-1',
        type: 'activity',
        label: 'Filter 1',
        value: {},
      };

      const filter2: AppliedFilter = {
        id: 'filter-2',
        type: 'timeRange',
        label: 'Filter 2',
        value: {},
      };

      act(() => {
        result.current.addFilter(filter1);
        result.current.addFilter(filter2);
      });

      expect(result.current.filters).toHaveLength(2);
      expect(result.current.filterCount).toBe(2);
    });
  });

  describe('removeFilter', () => {
    it('removes a filter by ID', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'filter-1', type: 'activity', label: 'Filter 1', value: {} },
        { id: 'filter-2', type: 'timeRange', label: 'Filter 2', value: {} },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      act(() => {
        result.current.removeFilter('filter-1');
      });

      expect(result.current.filters).toHaveLength(1);
      expect(result.current.filters[0].id).toBe('filter-2');
    });

    it('handles removing non-existent filter gracefully', () => {
      const { result } = renderHook(() => useExplorerFilters({ syncToUrl: false }), {
        wrapper: createWrapper(),
      });

      act(() => {
        result.current.removeFilter('non-existent');
      });

      expect(result.current.filters).toEqual([]);
    });
  });

  describe('clearFilters', () => {
    it('removes all filters', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'filter-1', type: 'activity', label: 'Filter 1', value: {} },
        { id: 'filter-2', type: 'timeRange', label: 'Filter 2', value: {} },
        { id: 'filter-3', type: 'resource', label: 'Filter 3', value: {} },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      expect(result.current.filters).toHaveLength(3);

      act(() => {
        result.current.clearFilters();
      });

      expect(result.current.filters).toHaveLength(0);
      expect(result.current.filterCount).toBe(0);
    });
  });

  describe('setFilters', () => {
    it('replaces all filters', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'filter-1', type: 'activity', label: 'Filter 1', value: {} },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      const newFilters: AppliedFilter[] = [
        { id: 'new-1', type: 'performance', label: 'New Filter 1', value: {} },
        { id: 'new-2', type: 'rework', label: 'New Filter 2', value: {} },
      ];

      act(() => {
        result.current.setFilters(newFilters);
      });

      expect(result.current.filters).toHaveLength(2);
      expect(result.current.filters[0].id).toBe('new-1');
      expect(result.current.filters[1].id).toBe('new-2');
    });
  });

  describe('hasFilterType', () => {
    it('returns true when filter type exists', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'filter-1', type: 'activity', label: 'Activity Filter', value: {} },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      expect(result.current.hasFilterType('activity')).toBe(true);
      expect(result.current.hasFilterType('timeRange')).toBe(false);
    });
  });

  describe('getFiltersByType', () => {
    it('returns filters of specific type', () => {
      const initialFilters: AppliedFilter[] = [
        { id: 'filter-1', type: 'activity', label: 'Activity 1', value: {} },
        { id: 'filter-2', type: 'timeRange', label: 'Time Range', value: {} },
        { id: 'filter-3', type: 'activity', label: 'Activity 2', value: {} },
      ];

      const { result } = renderHook(
        () => useExplorerFilters({ initialFilters, syncToUrl: false }),
        { wrapper: createWrapper() }
      );

      const activityFilters = result.current.getFiltersByType('activity');
      expect(activityFilters).toHaveLength(2);
      expect(activityFilters[0].id).toBe('filter-1');
      expect(activityFilters[1].id).toBe('filter-3');
    });

    it('returns empty array when no filters of type exist', () => {
      const { result } = renderHook(() => useExplorerFilters({ syncToUrl: false }), {
        wrapper: createWrapper(),
      });

      const resourceFilters = result.current.getFiltersByType('resource');
      expect(resourceFilters).toEqual([]);
    });
  });

  describe('onFiltersChange callback', () => {
    it('calls callback when filters change', () => {
      const onFiltersChange = jest.fn();

      const { result } = renderHook(
        () => useExplorerFilters({ syncToUrl: false, onFiltersChange }),
        { wrapper: createWrapper() }
      );

      const newFilter: AppliedFilter = {
        id: 'filter-1',
        type: 'activity',
        label: 'Test',
        value: {},
      };

      act(() => {
        result.current.addFilter(newFilter);
      });

      expect(onFiltersChange).toHaveBeenCalledWith([newFilter]);
    });
  });
});
