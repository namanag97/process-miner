/**
 * Selection Store Tests
 */

import { act, renderHook } from '@testing-library/react';
import {
  useSelectionStore,
  selectSelectedNode,
  selectSelectedEdge,
  selectSelectedVariant,
} from '../selectionStore';

// Reset store between tests
beforeEach(() => {
  act(() => {
    useSelectionStore.getState().clearSelection();
  });
});

describe('selectionStore', () => {
  describe('initial state', () => {
    it('should have null selections initially', () => {
      const { result } = renderHook(() => useSelectionStore());
      expect(result.current.selectedNodeId).toBeNull();
      expect(result.current.selectedEdgeId).toBeNull();
      expect(result.current.selectedVariantKey).toBeNull();
      expect(result.current.selectedActivityId).toBeNull();
      expect(result.current.hoveredNodeId).toBeNull();
    });
  });

  describe('selectNode', () => {
    it('should select a node', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
      });

      expect(result.current.selectedNodeId).toBe('node-123');
    });

    it('should clear edge selection when node is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectEdge('edge-1-2');
        result.current.selectNode('node-123');
      });

      expect(result.current.selectedNodeId).toBe('node-123');
      expect(result.current.selectedEdgeId).toBeNull();
    });

    it('should clear node selection when selecting null', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
        result.current.selectNode(null);
      });

      expect(result.current.selectedNodeId).toBeNull();
    });
  });

  describe('selectEdge', () => {
    it('should select an edge', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectEdge('edge-A-B-0');
      });

      expect(result.current.selectedEdgeId).toBe('edge-A-B-0');
    });

    it('should clear node selection when edge is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
        result.current.selectEdge('edge-A-B-0');
      });

      expect(result.current.selectedEdgeId).toBe('edge-A-B-0');
      expect(result.current.selectedNodeId).toBeNull();
    });
  });

  describe('selectVariant', () => {
    it('should select a variant', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectVariant('variant-key-123');
      });

      expect(result.current.selectedVariantKey).toBe('variant-key-123');
    });

    it('should not clear node/edge selection when variant is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
        result.current.selectVariant('variant-key');
      });

      expect(result.current.selectedNodeId).toBe('node-123');
      expect(result.current.selectedVariantKey).toBe('variant-key');
    });
  });

  describe('selectActivity', () => {
    it('should select an activity', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectActivity('activity-123');
      });

      expect(result.current.selectedActivityId).toBe('activity-123');
    });
  });

  describe('setHoveredNode', () => {
    it('should set hovered node', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.setHoveredNode('node-hover');
      });

      expect(result.current.hoveredNodeId).toBe('node-hover');
    });

    it('should clear hovered node', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.setHoveredNode('node-hover');
        result.current.setHoveredNode(null);
      });

      expect(result.current.hoveredNodeId).toBeNull();
    });
  });

  describe('clearSelection', () => {
    it('should clear all selections', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
        result.current.selectVariant('variant-key');
        result.current.selectActivity('activity-456');
        result.current.setHoveredNode('hover-node');
      });

      act(() => {
        result.current.clearSelection();
      });

      expect(result.current.selectedNodeId).toBeNull();
      expect(result.current.selectedEdgeId).toBeNull();
      expect(result.current.selectedVariantKey).toBeNull();
      expect(result.current.selectedActivityId).toBeNull();
      expect(result.current.hoveredNodeId).toBeNull();
    });
  });

  describe('hasSelection', () => {
    it('should return false when nothing is selected', () => {
      const { result } = renderHook(() => useSelectionStore());
      expect(result.current.hasSelection()).toBe(false);
    });

    it('should return true when node is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectNode('node-123');
      });

      expect(result.current.hasSelection()).toBe(true);
    });

    it('should return true when edge is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectEdge('edge-1');
      });

      expect(result.current.hasSelection()).toBe(true);
    });

    it('should return true when variant is selected', () => {
      const { result } = renderHook(() => useSelectionStore());

      act(() => {
        result.current.selectVariant('variant-key');
      });

      expect(result.current.hasSelection()).toBe(true);
    });
  });

  describe('selectors', () => {
    it('selectSelectedNode returns node id', () => {
      act(() => {
        useSelectionStore.getState().selectNode('node-123');
      });

      expect(selectSelectedNode(useSelectionStore.getState())).toBe('node-123');
    });

    it('selectSelectedEdge returns edge id', () => {
      act(() => {
        useSelectionStore.getState().selectEdge('edge-A-B');
      });

      expect(selectSelectedEdge(useSelectionStore.getState())).toBe('edge-A-B');
    });

    it('selectSelectedVariant returns variant key', () => {
      act(() => {
        useSelectionStore.getState().selectVariant('variant-key');
      });

      expect(selectSelectedVariant(useSelectionStore.getState())).toBe('variant-key');
    });
  });
});
