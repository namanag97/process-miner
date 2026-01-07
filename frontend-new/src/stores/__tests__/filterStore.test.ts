/**
 * Filter Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import { useFilterStore, selectFilters, selectFilterCount, selectHasFilters } from '../filterStore';
import type { AppliedFilter } from '../../features/explorer/types';

// Reset store between tests
beforeEach(() => {
  act(() => {
    useFilterStore.getState().clearFilters();
  });
});

describe('filterStore', () => {
  describe('initial state', () => {
    it('should have empty filters initially', () => {
      const { result } = renderHook(() => useFilterStore());
      expect(result.current.filters).toEqual([]);
    });
  });

  describe('addFilter', () => {
    it('should add a filter to the store', () => {
      const { result } = renderHook(() => useFilterStore());

      const filter: AppliedFilter = {
        id: 'test-1',
        type: 'activity',
        label: 'With: Order Created',
        value: { mode: 'include', activities: ['Order Created'] },
        color: 'green',
      };

      act(() => {
        result.current.addFilter(filter);
      });

      expect(result.current.filters).toHaveLength(1);
      expect(result.current.filters[0]).toEqual(filter);
    });

    it('should add multiple filters', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Activity 1',
          value: {},
        });
        result.current.addFilter({
          id: 'test-2',
          type: 'timeRange',
          label: 'Time Range',
          value: {},
        });
      });

      expect(result.current.filters).toHaveLength(2);
    });
  });

  describe('removeFilter', () => {
    it('should remove a filter by id', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test',
          value: {},
        });
        result.current.addFilter({
          id: 'test-2',
          type: 'timeRange',
          label: 'Test 2',
          value: {},
        });
      });

      act(() => {
        result.current.removeFilter('test-1');
      });

      expect(result.current.filters).toHaveLength(1);
      expect(result.current.filters[0].id).toBe('test-2');
    });

    it('should do nothing if filter id not found', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test',
          value: {},
        });
      });

      act(() => {
        result.current.removeFilter('non-existent');
      });

      expect(result.current.filters).toHaveLength(1);
    });
  });

  describe('updateFilter', () => {
    it('should update a filter by id', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Original',
          value: { activities: ['A'] },
        });
      });

      act(() => {
        result.current.updateFilter('test-1', {
          label: 'Updated',
          value: { activities: ['A', 'B'] },
        });
      });

      expect(result.current.filters[0].label).toBe('Updated');
      expect(result.current.filters[0].value).toEqual({ activities: ['A', 'B'] });
    });
  });

  describe('clearFilters', () => {
    it('should clear all filters', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({ id: '1', type: 'activity', label: 'A', value: {} });
        result.current.addFilter({ id: '2', type: 'activity', label: 'B', value: {} });
        result.current.addFilter({ id: '3', type: 'timeRange', label: 'C', value: {} });
      });

      expect(result.current.filters).toHaveLength(3);

      act(() => {
        result.current.clearFilters();
      });

      expect(result.current.filters).toHaveLength(0);
    });
  });

  describe('setFilters', () => {
    it('should replace all filters', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({ id: 'old', type: 'activity', label: 'Old', value: {} });
      });

      const newFilters: AppliedFilter[] = [
        { id: 'new-1', type: 'timeRange', label: 'New 1', value: {} },
        { id: 'new-2', type: 'performance', label: 'New 2', value: {} },
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
    it('should return true if filter type exists', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({
          id: 'test',
          type: 'performance',
          label: 'Test',
          value: {},
        });
      });

      expect(result.current.hasFilterType('performance')).toBe(true);
      expect(result.current.hasFilterType('activity')).toBe(false);
    });
  });

  describe('getFiltersByType', () => {
    it('should return filters of specified type', () => {
      const { result } = renderHook(() => useFilterStore());

      act(() => {
        result.current.addFilter({ id: '1', type: 'activity', label: 'A1', value: {} });
        result.current.addFilter({ id: '2', type: 'activity', label: 'A2', value: {} });
        result.current.addFilter({ id: '3', type: 'timeRange', label: 'T1', value: {} });
      });

      const activityFilters = result.current.getFiltersByType('activity');
      expect(activityFilters).toHaveLength(2);
      expect(activityFilters.every((f) => f.type === 'activity')).toBe(true);
    });
  });

  describe('selectors', () => {
    it('selectFilters returns filters array', () => {
      const state = useFilterStore.getState();
      expect(selectFilters(state)).toEqual([]);

      act(() => {
        useFilterStore.getState().addFilter({
          id: 'test',
          type: 'activity',
          label: 'Test',
          value: {},
        });
      });

      expect(selectFilters(useFilterStore.getState())).toHaveLength(1);
    });

    it('selectFilterCount returns count', () => {
      act(() => {
        useFilterStore.getState().addFilter({ id: '1', type: 'activity', label: 'A', value: {} });
        useFilterStore.getState().addFilter({ id: '2', type: 'activity', label: 'B', value: {} });
      });

      expect(selectFilterCount(useFilterStore.getState())).toBe(2);
    });

    it('selectHasFilters returns boolean', () => {
      expect(selectHasFilters(useFilterStore.getState())).toBe(false);

      act(() => {
        useFilterStore.getState().addFilter({ id: '1', type: 'activity', label: 'A', value: {} });
      });

      expect(selectHasFilters(useFilterStore.getState())).toBe(true);
    });
  });
});
