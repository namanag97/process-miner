/**
 * useExplorerState - State management for Process Explorer page
 * Manages selection, filters, and UI state for the explorer
 */

import { useState, useCallback, useMemo } from 'react';

export interface ExplorerFilters {
  minFrequency?: number;
  maxFrequency?: number;
  selectedActivities?: string[];
  variantFilter?: 'all' | 'rework' | 'no-rework';
  dateRange?: { start: string; end: string };
}

export interface ExplorerSelection {
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  selectedVariantKey: string | null;
  selectedActivityId: string | null;
}

export interface ExplorerUIState {
  layout: 'horizontal' | 'vertical';
  showFilters: boolean;
  showVariants: boolean;
  showMetrics: boolean;
  zoomLevel: number;
}

export interface ExplorerState {
  selection: ExplorerSelection;
  filters: ExplorerFilters;
  ui: ExplorerUIState;
}

const DEFAULT_SELECTION: ExplorerSelection = {
  selectedNodeId: null,
  selectedEdgeId: null,
  selectedVariantKey: null,
  selectedActivityId: null,
};

const DEFAULT_FILTERS: ExplorerFilters = {
  minFrequency: undefined,
  maxFrequency: undefined,
  selectedActivities: [],
  variantFilter: 'all',
  dateRange: undefined,
};

const DEFAULT_UI: ExplorerUIState = {
  layout: 'horizontal',
  showFilters: true,
  showVariants: true,
  showMetrics: true,
  zoomLevel: 1,
};

/**
 * Hook for managing Process Explorer state
 * 
 * @example
 * ```tsx
 * const explorer = useExplorerState();
 * 
 * // Access state
 * explorer.selection.selectedNodeId
 * explorer.filters.minFrequency
 * explorer.ui.layout
 * 
 * // Update state
 * explorer.selectNode('node-123');
 * explorer.setFilters({ minFrequency: 10 });
 * explorer.toggleFilters();
 * ```
 */
export function useExplorerState(initialState?: Partial<ExplorerState>) {
  // Selection state
  const [selection, setSelection] = useState<ExplorerSelection>({
    ...DEFAULT_SELECTION,
    ...initialState?.selection,
  });

  // Filters state
  const [filters, setFilters] = useState<ExplorerFilters>({
    ...DEFAULT_FILTERS,
    ...initialState?.filters,
  });

  // UI state
  const [ui, setUI] = useState<ExplorerUIState>({
    ...DEFAULT_UI,
    ...initialState?.ui,
  });

  // Selection actions
  const selectNode = useCallback((nodeId: string | null) => {
    setSelection((prev) => ({
      ...prev,
      selectedNodeId: nodeId,
      selectedEdgeId: null, // Clear edge when node selected
    }));
  }, []);

  const selectEdge = useCallback((edgeId: string | null) => {
    setSelection((prev) => ({
      ...prev,
      selectedEdgeId: edgeId,
      selectedNodeId: null, // Clear node when edge selected
    }));
  }, []);

  const selectVariant = useCallback((variantKey: string | null) => {
    setSelection((prev) => ({
      ...prev,
      selectedVariantKey: variantKey,
    }));
  }, []);

  const selectActivity = useCallback((activityId: string | null) => {
    setSelection((prev) => ({
      ...prev,
      selectedActivityId: activityId,
    }));
  }, []);

  const clearSelection = useCallback(() => {
    setSelection(DEFAULT_SELECTION);
  }, []);

  // Filter actions
  const updateFilters = useCallback((updates: Partial<ExplorerFilters>) => {
    setFilters((prev) => ({ ...prev, ...updates }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS);
  }, []);

  const toggleActivityFilter = useCallback((activity: string) => {
    setFilters((prev) => {
      const current = prev.selectedActivities ?? [];
      const isSelected = current.includes(activity);
      
      return {
        ...prev,
        selectedActivities: isSelected
          ? current.filter((a) => a !== activity)
          : [...current, activity],
      };
    });
  }, []);

  // UI actions
  const updateUI = useCallback((updates: Partial<ExplorerUIState>) => {
    setUI((prev) => ({ ...prev, ...updates }));
  }, []);

  const toggleFilters = useCallback(() => {
    setUI((prev) => ({ ...prev, showFilters: !prev.showFilters }));
  }, []);

  const toggleVariants = useCallback(() => {
    setUI((prev) => ({ ...prev, showVariants: !prev.showVariants }));
  }, []);

  const toggleMetrics = useCallback(() => {
    setUI((prev) => ({ ...prev, showMetrics: !prev.showMetrics }));
  }, []);

  const setLayout = useCallback((layout: 'horizontal' | 'vertical') => {
    setUI((prev) => ({ ...prev, layout }));
  }, []);

  const setZoom = useCallback((zoomLevel: number) => {
    setUI((prev) => ({ ...prev, zoomLevel: Math.max(0.1, Math.min(2, zoomLevel)) }));
  }, []);

  const zoomIn = useCallback(() => {
    setUI((prev) => ({ ...prev, zoomLevel: Math.min(2, prev.zoomLevel + 0.1) }));
  }, []);

  const zoomOut = useCallback(() => {
    setUI((prev) => ({ ...prev, zoomLevel: Math.max(0.1, prev.zoomLevel - 0.1) }));
  }, []);

  const resetZoom = useCallback(() => {
    setUI((prev) => ({ ...prev, zoomLevel: 1 }));
  }, []);

  // Reset all state
  const reset = useCallback(() => {
    setSelection(DEFAULT_SELECTION);
    setFilters(DEFAULT_FILTERS);
    setUI(DEFAULT_UI);
  }, []);

  // Computed values
  const hasActiveFilters = useMemo(() => {
    return (
      filters.minFrequency !== undefined ||
      filters.maxFrequency !== undefined ||
      (filters.selectedActivities?.length ?? 0) > 0 ||
      filters.variantFilter !== 'all' ||
      filters.dateRange !== undefined
    );
  }, [filters]);

  const hasSelection = useMemo(() => {
    return (
      selection.selectedNodeId !== null ||
      selection.selectedEdgeId !== null ||
      selection.selectedVariantKey !== null
    );
  }, [selection]);

  return {
    // State
    selection,
    filters,
    ui,
    
    // Selection actions
    selectNode,
    selectEdge,
    selectVariant,
    selectActivity,
    clearSelection,
    
    // Filter actions
    setFilters: updateFilters,
    clearFilters,
    toggleActivityFilter,
    
    // UI actions
    setUI: updateUI,
    toggleFilters,
    toggleVariants,
    toggleMetrics,
    setLayout,
    setZoom,
    zoomIn,
    zoomOut,
    resetZoom,
    
    // Reset
    reset,
    
    // Computed
    hasActiveFilters,
    hasSelection,
  };
}

export type UseExplorerStateReturn = ReturnType<typeof useExplorerState>;
