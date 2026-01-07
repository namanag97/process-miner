/**
 * useAnalyticsFilters - URL State Management for Analytics Page
 *
 * This hook manages filter and tab state in the URL, enabling:
 * - Shareable analytics configurations via URL
 * - Browser back/forward navigation
 * - Persistent state across page refreshes
 *
 * URL Parameters:
 * - datasetId: Selected dataset/log ID
 * - tab: Active analytics tab (performance, conformance, rework, resources)
 * - dateRange: Date range filter (start,end ISO strings)
 * - metric: Selected metric for comparison
 *
 * @example
 * const { datasetId, tab, setDatasetId, setTab, dateRange, setDateRange } = useAnalyticsFilters();
 */

import { useCallback, useMemo } from 'react';
import { useSearchParams, useNavigate, useLocation, useParams } from 'react-router-dom';
import { createLogger } from '../../../shared/lib/logger';

const log = createLogger('useAnalyticsFilters');

export type AnalyticsTab = 'performance' | 'conformance' | 'rework' | 'resources';

export interface DateRange {
  start: string;
  end: string;
}

export interface AnalyticsFiltersState {
  datasetId: string | null;
  tab: AnalyticsTab;
  dateRange: DateRange | null;
  metric: string | null;
}

export interface UseAnalyticsFiltersReturn {
  /** Current selected dataset ID */
  datasetId: string | null;
  /** Current active tab */
  tab: AnalyticsTab;
  /** Current date range filter */
  dateRange: DateRange | null;
  /** Current selected metric */
  metric: string | null;
  /** Set the selected dataset */
  setDatasetId: (id: string) => void;
  /** Set the active tab */
  setTab: (tab: AnalyticsTab) => void;
  /** Set the date range filter */
  setDateRange: (range: DateRange | null) => void;
  /** Set the selected metric */
  setMetric: (metric: string | null) => void;
  /** Clear all filters */
  clearFilters: () => void;
  /** Get shareable URL for current state */
  getShareableUrl: () => string;
  /** Project ID from route params (if workspace-scoped) */
  projectId: string | null;
}

const VALID_TABS: AnalyticsTab[] = ['performance', 'conformance', 'rework', 'resources'];

function isValidTab(value: string | null): value is AnalyticsTab {
  return value !== null && VALID_TABS.includes(value as AnalyticsTab);
}

function parseTabFromPath(pathname: string): AnalyticsTab {
  const segments = pathname.split('/').filter(Boolean);
  const lastSegment = segments[segments.length - 1];

  if (isValidTab(lastSegment)) {
    return lastSegment;
  }

  // Check for workspace-scoped routes
  const analyticsIndex = segments.indexOf('analytics');
  if (analyticsIndex >= 0 && analyticsIndex < segments.length - 1) {
    const tabSegment = segments[analyticsIndex + 1];
    if (isValidTab(tabSegment)) {
      return tabSegment;
    }
  }

  return 'performance';
}

function parseDateRange(value: string | null): DateRange | null {
  if (!value) return null;
  try {
    const [start, end] = value.split(',');
    if (start && end) {
      return { start, end };
    }
    return null;
  } catch {
    return null;
  }
}

function serializeDateRange(range: DateRange | null): string | null {
  if (!range) return null;
  return `${range.start},${range.end}`;
}

export function useAnalyticsFilters(): UseAnalyticsFiltersReturn {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { projectId } = useParams<{ projectId?: string }>();

  // Parse current state from URL
  const state = useMemo((): AnalyticsFiltersState => {
    return {
      datasetId: searchParams.get('datasetId'),
      tab: parseTabFromPath(location.pathname),
      dateRange: parseDateRange(searchParams.get('dateRange')),
      metric: searchParams.get('metric'),
    };
  }, [searchParams, location.pathname]);

  // Navigate to a new tab
  const setTab = useCallback(
    (newTab: AnalyticsTab) => {
      if (newTab === state.tab) return;

      log.debug('Tab changed', { from: state.tab, to: newTab });

      // Build new path
      let newPath: string;
      if (projectId) {
        // Workspace-scoped navigation
        newPath =
          newTab === 'performance'
            ? `/workspace/${projectId}/analytics`
            : `/workspace/${projectId}/analytics/${newTab}`;
      } else {
        // Standalone navigation
        newPath =
          newTab === 'performance' ? '/analytics' : `/analytics/${newTab}`;
      }

      // Preserve query params
      const queryString = searchParams.toString();
      navigate(queryString ? `${newPath}?${queryString}` : newPath);
    },
    [state.tab, projectId, searchParams, navigate]
  );

  // Set dataset ID in URL
  const setDatasetId = useCallback(
    (id: string) => {
      log.debug('Dataset changed', { datasetId: id });
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          next.set('datasetId', id);
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  // Set date range in URL
  const setDateRange = useCallback(
    (range: DateRange | null) => {
      log.debug('Date range changed', { range });
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          const serialized = serializeDateRange(range);
          if (serialized) {
            next.set('dateRange', serialized);
          } else {
            next.delete('dateRange');
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  // Set metric in URL
  const setMetric = useCallback(
    (metric: string | null) => {
      log.debug('Metric changed', { metric });
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (metric) {
            next.set('metric', metric);
          } else {
            next.delete('metric');
          }
          return next;
        },
        { replace: true }
      );
    },
    [setSearchParams]
  );

  // Clear all filters
  const clearFilters = useCallback(() => {
    log.info('All filters cleared');
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete('dateRange');
        next.delete('metric');
        // Keep datasetId as it's a selection, not a filter
        return next;
      },
      { replace: true }
    );
  }, [setSearchParams]);

  // Get shareable URL
  const getShareableUrl = useCallback(() => {
    return `${window.location.origin}${location.pathname}${location.search}`;
  }, [location]);

  return {
    datasetId: state.datasetId,
    tab: state.tab,
    dateRange: state.dateRange,
    metric: state.metric,
    setDatasetId,
    setTab,
    setDateRange,
    setMetric,
    clearFilters,
    getShareableUrl,
    projectId: projectId ?? null,
  };
}

export default useAnalyticsFilters;
