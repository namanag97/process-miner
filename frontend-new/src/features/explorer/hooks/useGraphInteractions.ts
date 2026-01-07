/**
 * useGraphInteractions Hook
 *
 * Provides optimized event handlers for graph interactions with:
 * - Throttled hover events for smooth performance
 * - Debounced selection for rapid clicks
 * - RAF-based viewport updates
 * - Cleanup on unmount
 */

import { useEffect, useRef, useCallback } from 'react';
import type { Core, EventObject } from 'cytoscape';
import { throttle, rafThrottle, debounce } from '../../../shared/lib/performanceUtils';

export interface GraphInteractionConfig {
  onNodeHover?: (nodeId: string | null) => void;
  onNodeSelect?: (nodeId: string, multiSelect?: boolean) => void;
  onEdgeHover?: (edgeId: string | null) => void;
  onEdgeSelect?: (edgeId: string, source: string, target: string) => void;
  onViewportChange?: (extent: { x1: number; y1: number; x2: number; y2: number }) => void;
  onZoomChange?: (zoom: number) => void;
  hoverThrottleMs?: number;
  selectionDebounceMs?: number;
}

export interface UseGraphInteractionsReturn {
  attachHandlers: (cy: Core) => void;
  detachHandlers: () => void;
}

/**
 * Hook for optimized graph interactions
 */
export function useGraphInteractions(
  config: GraphInteractionConfig
): UseGraphInteractionsReturn {
  const {
    onNodeHover,
    onNodeSelect,
    onEdgeHover,
    onEdgeSelect,
    onViewportChange,
    onZoomChange,
    hoverThrottleMs = 50,
    selectionDebounceMs = 100,
  } = config;

  const cyRef = useRef<Core | null>(null);
  const handlersRef = useRef<{
    nodeMouseOver?: ReturnType<typeof throttle>;
    nodeMouseOut?: ReturnType<typeof throttle>;
    edgeMouseOver?: ReturnType<typeof throttle>;
    edgeMouseOut?: ReturnType<typeof throttle>;
    nodeClick?: ReturnType<typeof debounce>;
    edgeClick?: ReturnType<typeof debounce>;
    viewport?: ReturnType<typeof rafThrottle>;
    zoom?: ReturnType<typeof throttle>;
  }>({});

  // Create throttled/debounced handlers
  const createHandlers = useCallback(() => {
    // Node hover (throttled)
    if (onNodeHover) {
      handlersRef.current.nodeMouseOver = throttle((e: EventObject) => {
        if (e.target.isNode()) {
          onNodeHover(e.target.id());
        }
      }, hoverThrottleMs);

      handlersRef.current.nodeMouseOut = throttle(() => {
        onNodeHover(null);
      }, hoverThrottleMs);
    }

    // Edge hover (throttled)
    if (onEdgeHover) {
      handlersRef.current.edgeMouseOver = throttle((e: EventObject) => {
        if (e.target.isEdge()) {
          onEdgeHover(e.target.id());
        }
      }, hoverThrottleMs);

      handlersRef.current.edgeMouseOut = throttle(() => {
        onEdgeHover(null);
      }, hoverThrottleMs);
    }

    // Node click (debounced for rapid clicks)
    if (onNodeSelect) {
      handlersRef.current.nodeClick = debounce((e: EventObject) => {
        if (e.target.isNode()) {
          const shiftKey = (e.originalEvent as MouseEvent)?.shiftKey ?? false;
          onNodeSelect(e.target.id(), shiftKey);
        }
      }, selectionDebounceMs, { leading: true, trailing: false });
    }

    // Edge click (debounced)
    if (onEdgeSelect) {
      handlersRef.current.edgeClick = debounce((e: EventObject) => {
        if (e.target.isEdge()) {
          const edge = e.target;
          onEdgeSelect(edge.id(), edge.source().id(), edge.target().id());
        }
      }, selectionDebounceMs, { leading: true, trailing: false });
    }

    // Viewport changes (RAF throttled for smooth updates)
    if (onViewportChange) {
      handlersRef.current.viewport = rafThrottle(() => {
        if (cyRef.current) {
          const extent = cyRef.current.extent();
          onViewportChange(extent);
        }
      });
    }

    // Zoom changes (throttled)
    if (onZoomChange) {
      handlersRef.current.zoom = throttle(() => {
        if (cyRef.current) {
          onZoomChange(cyRef.current.zoom());
        }
      }, 100);
    }
  }, [
    onNodeHover,
    onNodeSelect,
    onEdgeHover,
    onEdgeSelect,
    onViewportChange,
    onZoomChange,
    hoverThrottleMs,
    selectionDebounceMs,
  ]);

  // Attach handlers to Cytoscape instance
  const attachHandlers = useCallback((cy: Core) => {
    cyRef.current = cy;
    createHandlers();

    const handlers = handlersRef.current;

    if (handlers.nodeMouseOver) {
      cy.on('mouseover', 'node', handlers.nodeMouseOver);
    }
    if (handlers.nodeMouseOut) {
      cy.on('mouseout', 'node', handlers.nodeMouseOut);
    }
    if (handlers.edgeMouseOver) {
      cy.on('mouseover', 'edge', handlers.edgeMouseOver);
    }
    if (handlers.edgeMouseOut) {
      cy.on('mouseout', 'edge', handlers.edgeMouseOut);
    }
    if (handlers.nodeClick) {
      cy.on('tap', 'node', handlers.nodeClick);
    }
    if (handlers.edgeClick) {
      cy.on('tap', 'edge', handlers.edgeClick);
    }
    if (handlers.viewport) {
      cy.on('viewport', handlers.viewport);
    }
    if (handlers.zoom) {
      cy.on('zoom', handlers.zoom);
    }
  }, [createHandlers]);

  // Detach handlers and cleanup
  const detachHandlers = useCallback(() => {
    const cy = cyRef.current;
    const handlers = handlersRef.current;

    if (cy) {
      if (handlers.nodeMouseOver) {
        cy.off('mouseover', 'node', handlers.nodeMouseOver);
        handlers.nodeMouseOver.cancel();
      }
      if (handlers.nodeMouseOut) {
        cy.off('mouseout', 'node', handlers.nodeMouseOut);
        handlers.nodeMouseOut.cancel();
      }
      if (handlers.edgeMouseOver) {
        cy.off('mouseover', 'edge', handlers.edgeMouseOver);
        handlers.edgeMouseOver.cancel();
      }
      if (handlers.edgeMouseOut) {
        cy.off('mouseout', 'edge', handlers.edgeMouseOut);
        handlers.edgeMouseOut.cancel();
      }
      if (handlers.nodeClick) {
        cy.off('tap', 'node', handlers.nodeClick);
        handlers.nodeClick.cancel();
      }
      if (handlers.edgeClick) {
        cy.off('tap', 'edge', handlers.edgeClick);
        handlers.edgeClick.cancel();
      }
      if (handlers.viewport) {
        cy.off('viewport', handlers.viewport);
        handlers.viewport.cancel();
      }
      if (handlers.zoom) {
        cy.off('zoom', handlers.zoom);
        handlers.zoom.cancel();
      }
    }

    cyRef.current = null;
    handlersRef.current = {};
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      detachHandlers();
    };
  }, [detachHandlers]);

  return {
    attachHandlers,
    detachHandlers,
  };
}

export default useGraphInteractions;
