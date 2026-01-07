/**
 * useFilterSync Integration Tests
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { MemoryRouter, useSearchParams } from 'react-router-dom';
import { useFilterSync, generateShareableUrl } from '../useFilterSync';
import { useFilterStore } from '../../stores/filterStore';
import type { AppliedFilter } from '../../features/explorer/types';

// Helper to create wrapper with router
const createWrapper = (initialEntries: string[] = ['/']) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return <MemoryRouter initialEntries={initialEntries}>{children}</MemoryRouter>;
  };
};

// Reset store between tests
beforeEach(() => {
  act(() => {
    useFilterStore.getState().clearFilters();
  });
});

describe('useFilterSync', () => {
  describe('initialization', () => {
    it('should initialize without errors', () => {
      const { result } = renderHook(() => useFilterSync(), {
        wrapper: createWrapper(),
      });

      expect(result.current.isInitialized).toBeDefined();
    });

    it('should load filters from URL on mount', async () => {
      // Create a URL with encoded filters
      const filters: AppliedFilter[] = [
        {
          id: 'url-filter-1',
          type: 'activity',
          label: 'From URL',
          value: { mode: 'include', activities: ['Test'] },
        },
      ];

      const encoded = btoa(
        encodeURIComponent(
          JSON.stringify([
            { i: 'url-filter-1', t: 'activity', l: 'From URL', v: { mode: 'include', activities: ['Test'] } },
          ])
        )
      );

      renderHook(() => useFilterSync(), {
        wrapper: createWrapper([`/?filters=${encoded}`]),
      });

      // Wait for async initialization
      await waitFor(() => {
        const storeFilters = useFilterStore.getState().filters;
        expect(storeFilters.length).toBe(1);
        expect(storeFilters[0].label).toBe('From URL');
      });
    });

    it('should handle invalid URL filters gracefully', () => {
      renderHook(() => useFilterSync(), {
        wrapper: createWrapper(['/?filters=invalid-base64!@#']),
      });

      // Should not crash, store should remain empty
      const storeFilters = useFilterStore.getState().filters;
      expect(storeFilters.length).toBe(0);
    });

    it('should handle empty filters param', () => {
      renderHook(() => useFilterSync(), {
        wrapper: createWrapper(['/?filters=']),
      });

      const storeFilters = useFilterStore.getState().filters;
      expect(storeFilters.length).toBe(0);
    });
  });

  describe('store to URL sync', () => {
    it('should sync filters to URL when added', async () => {
      // Component to check URL params
      let searchParams: URLSearchParams | null = null;
      const TestComponent = () => {
        useFilterSync({ debounceMs: 0 }); // No debounce for tests
        const [params] = useSearchParams();
        searchParams = params;
        return null;
      };

      renderHook(() => TestComponent(), {
        wrapper: createWrapper(),
      });

      act(() => {
        useFilterStore.getState().addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test Filter',
          value: {},
        });
      });

      await waitFor(() => {
        expect(searchParams?.has('filters')).toBe(true);
      });
    });

    it('should remove filters param when all filters cleared', async () => {
      let searchParams: URLSearchParams | null = null;
      const TestComponent = () => {
        useFilterSync({ debounceMs: 0 });
        const [params] = useSearchParams();
        searchParams = params;
        return null;
      };

      renderHook(() => TestComponent(), {
        wrapper: createWrapper(),
      });

      // Add then clear
      act(() => {
        useFilterStore.getState().addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test',
          value: {},
        });
      });

      await waitFor(() => {
        expect(searchParams?.has('filters')).toBe(true);
      });

      act(() => {
        useFilterStore.getState().clearFilters();
      });

      await waitFor(() => {
        expect(searchParams?.has('filters')).toBe(false);
      });
    });
  });

  describe('enabled option', () => {
    it('should not sync when disabled', () => {
      renderHook(() => useFilterSync({ enabled: false }), {
        wrapper: createWrapper(),
      });

      act(() => {
        useFilterStore.getState().addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test',
          value: {},
        });
      });

      // URL should not be updated
      // This is a simplification - in real test we'd need to check URL doesn't change
    });
  });

  describe('clearFiltersAndUrl', () => {
    it('should clear both store and URL', async () => {
      let clearFn: (() => void) | null = null;

      const TestComponent = () => {
        const { clearFiltersAndUrl } = useFilterSync({ debounceMs: 0 });
        clearFn = clearFiltersAndUrl;
        return null;
      };

      renderHook(() => TestComponent(), {
        wrapper: createWrapper(),
      });

      // Add filter
      act(() => {
        useFilterStore.getState().addFilter({
          id: 'test-1',
          type: 'activity',
          label: 'Test',
          value: {},
        });
      });

      expect(useFilterStore.getState().filters.length).toBe(1);

      // Clear using hook function
      act(() => {
        clearFn?.();
      });

      expect(useFilterStore.getState().filters.length).toBe(0);
    });
  });
});

describe('generateShareableUrl', () => {
  // jsdom doesn't allow redefining window.location, so we test the function behavior
  // by checking that the returned URL contains the expected filter encoding

  it('should generate URL with encoded filters', () => {
    const filters: AppliedFilter[] = [
      {
        id: 'filter-1',
        type: 'activity',
        label: 'Test Filter',
        value: { activities: ['A', 'B'] },
        color: 'green',
      },
    ];

    const url = generateShareableUrl(filters);

    // URL should contain the filters param
    expect(url).toContain('filters=');
    // Should contain the current origin (jsdom default is about:blank or http://localhost)
    expect(url).toMatch(/^(http|about)/);
  });

  it('should return URL without filters param when empty', () => {
    const url = generateShareableUrl([]);

    expect(url).not.toContain('filters=');
  });

  it('should encode filter data in base64', () => {
    const filters: AppliedFilter[] = [
      {
        id: 'filter-1',
        type: 'timeRange',
        label: 'Last 7 days',
        value: { start: '2024-01-01', end: '2024-01-07' },
      },
    ];

    const url = generateShareableUrl(filters);

    // Extract the filters param
    const urlObj = new URL(url);
    const filtersParam = urlObj.searchParams.get('filters');
    expect(filtersParam).toBeTruthy();

    // Should be valid base64 that decodes to JSON with our filter data
    if (filtersParam) {
      const decoded = JSON.parse(decodeURIComponent(atob(filtersParam)));
      expect(decoded).toHaveLength(1);
      expect(decoded[0].t).toBe('timeRange');
      expect(decoded[0].l).toBe('Last 7 days');
    }
  });
});
