/**
 * Selection Store
 *
 * Manages graph selection state for the Explorer feature.
 * Tracks selected nodes, edges, variants, and activities.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface SelectionState {
  // State
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  selectedVariantKey: string | null;
  selectedActivityId: string | null;
  hoveredNodeId: string | null;

  // Actions
  selectNode: (nodeId: string | null) => void;
  selectEdge: (edgeId: string | null) => void;
  selectVariant: (variantKey: string | null) => void;
  selectActivity: (activityId: string | null) => void;
  setHoveredNode: (nodeId: string | null) => void;
  clearSelection: () => void;

  // Computed
  hasSelection: () => boolean;
}

const initialState = {
  selectedNodeId: null,
  selectedEdgeId: null,
  selectedVariantKey: null,
  selectedActivityId: null,
  hoveredNodeId: null,
};

export const useSelectionStore = create<SelectionState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      selectNode: (nodeId) =>
        set(
          {
            selectedNodeId: nodeId,
            selectedEdgeId: null, // Clear edge when node selected
          },
          false,
          'selection/selectNode'
        ),

      selectEdge: (edgeId) =>
        set(
          {
            selectedEdgeId: edgeId,
            selectedNodeId: null, // Clear node when edge selected
          },
          false,
          'selection/selectEdge'
        ),

      selectVariant: (variantKey) =>
        set({ selectedVariantKey: variantKey }, false, 'selection/selectVariant'),

      selectActivity: (activityId) =>
        set({ selectedActivityId: activityId }, false, 'selection/selectActivity'),

      setHoveredNode: (nodeId) =>
        set({ hoveredNodeId: nodeId }, false, 'selection/setHoveredNode'),

      clearSelection: () => set(initialState, false, 'selection/clear'),

      hasSelection: () => {
        const state = get();
        return !!(
          state.selectedNodeId ||
          state.selectedEdgeId ||
          state.selectedVariantKey
        );
      },
    }),
    { name: 'SelectionStore' }
  )
);

// Selectors
export const selectSelectedNode = (state: SelectionState) => state.selectedNodeId;
export const selectSelectedEdge = (state: SelectionState) => state.selectedEdgeId;
export const selectSelectedVariant = (state: SelectionState) => state.selectedVariantKey;
export const selectSelectedActivity = (state: SelectionState) => state.selectedActivityId;
export const selectHoveredNode = (state: SelectionState) => state.hoveredNodeId;
