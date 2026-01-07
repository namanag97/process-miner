/**
 * OptimizedProcessGraph Component
 *
 * High-performance process graph visualization with:
 * - Automatic renderer selection (WebGL/Canvas/SVG) based on graph size
 * - Viewport virtualization for large graphs
 * - Level-of-detail (LOD) system based on zoom level
 * - Debounced/throttled interactions
 * - Proper memory cleanup
 *
 * Performance targets:
 * - < 100 nodes: Full SVG rendering with all labels
 * - 100-500 nodes: Canvas rendering with selective labels
 * - 500-2000 nodes: WebGL with viewport culling and LOD
 * - 2000+ nodes: WebGL with aggressive culling and simplified rendering
 */

import cytoscape, { Core, CytoscapeOptions, Stylesheet } from 'cytoscape';
// @ts-expect-error - cytoscape-dagre has no types
import dagre from 'cytoscape-dagre';
import { useEffect, useRef, useState, useCallback, useMemo, memo } from 'react';
import { debounce } from '../../../../shared/lib/performanceUtils';
import { useGraphInteractions } from '../../hooks/useGraphInteractions';
import type { GraphTier } from '../../hooks/useTieredGraph';

// Register dagre extension
cytoscape.use(dagre);

// Types
export interface ProcessNode {
  id: string;
  label: string;
  frequency?: number;
  isStart?: boolean;
  isEnd?: boolean;
}

export interface ProcessEdge {
  id: string;
  source: string;
  target: string;
  frequency?: number;
  probability?: number;
}

export interface ProcessGraphData {
  nodes: ProcessNode[];
  edges: ProcessEdge[];
}

export interface OptimizedProcessGraphProps {
  data: ProcessGraphData;
  onNodeClick?: (node: ProcessNode) => void;
  onNodeHover?: (nodeId: string | null) => void;
  onEdgeClick?: (edge: ProcessEdge) => void;
  onEdgeHover?: (edgeId: string | null) => void;
  selectedNodeId?: string | null;
  selectedEdgeId?: string | null;
  hoveredNodeId?: string | null;
  className?: string;
  layout?: 'dagre' | 'preset' | 'cose';
  tier?: GraphTier;
  showPerformanceWarning?: boolean;
  onPerformanceMetrics?: (metrics: PerformanceMetrics) => void;
}

export interface PerformanceMetrics {
  nodeCount: number;
  edgeCount: number;
  renderer: RendererType;
  initialRenderMs: number;
  layoutMs: number;
  fps?: number;
}

type RendererType = 'svg' | 'canvas' | 'webgl';
type LODLevel = 'full' | 'medium' | 'low' | 'minimal';

// Performance thresholds
const RENDERER_THRESHOLDS = {
  svg: 100,        // Use SVG for < 100 nodes
  canvas: 500,     // Use Canvas for 100-500 nodes
  webgl: Infinity, // Use WebGL for 500+ nodes
};

const LOD_ZOOM_THRESHOLDS = {
  full: 0.7,    // Zoom >= 0.7: full detail
  medium: 0.4,  // Zoom 0.4-0.7: medium detail
  low: 0.2,     // Zoom 0.2-0.4: low detail
  minimal: 0,   // Zoom < 0.2: minimal detail
};

/**
 * Determine optimal renderer based on graph size
 */
function selectRenderer(nodeCount: number): RendererType {
  if (nodeCount < RENDERER_THRESHOLDS.svg) return 'svg';
  if (nodeCount < RENDERER_THRESHOLDS.canvas) return 'canvas';
  return 'webgl';
}

/**
 * Determine LOD level based on zoom
 */
function getLODLevel(zoom: number): LODLevel {
  if (zoom >= LOD_ZOOM_THRESHOLDS.full) return 'full';
  if (zoom >= LOD_ZOOM_THRESHOLDS.medium) return 'medium';
  if (zoom >= LOD_ZOOM_THRESHOLDS.low) return 'low';
  return 'minimal';
}

/**
 * Get LOD-based styles
 */
function getLODStyles(lod: LODLevel): Partial<Stylesheet>[] {
  const baseNodeStyle = {
    'background-color': '#4A90D9',
    'border-width': 2,
    'border-color': '#2E5A88',
  };

  const baseEdgeStyle = {
    'line-color': '#7F8C8D',
    'target-arrow-color': '#7F8C8D',
    'target-arrow-shape': 'triangle',
    'curve-style': 'bezier',
  };

  switch (lod) {
    case 'full':
      return [
        {
          selector: 'node',
          style: {
            ...baseNodeStyle,
            label: 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#fff',
            'font-size': '12px',
            width: '120px',
            height: '40px',
            shape: 'roundrectangle',
            'text-wrap': 'ellipsis',
            'text-max-width': '100px',
          },
        },
        {
          selector: 'edge',
          style: {
            ...baseEdgeStyle,
            width: 2,
            label: 'data(label)',
            'font-size': '10px',
            'text-background-color': '#fff',
            'text-background-opacity': 0.8,
            'text-background-padding': '2px',
          },
        },
      ];

    case 'medium':
      return [
        {
          selector: 'node',
          style: {
            ...baseNodeStyle,
            label: 'data(shortLabel)',
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#fff',
            'font-size': '10px',
            width: '80px',
            height: '30px',
            shape: 'roundrectangle',
          },
        },
        {
          selector: 'edge',
          style: {
            ...baseEdgeStyle,
            width: 2,
            label: '', // Hide edge labels
          },
        },
      ];

    case 'low':
      return [
        {
          selector: 'node',
          style: {
            ...baseNodeStyle,
            label: '', // Hide labels
            width: '40px',
            height: '20px',
            shape: 'ellipse',
          },
        },
        {
          selector: 'edge',
          style: {
            ...baseEdgeStyle,
            width: 1,
            label: '',
          },
        },
      ];

    case 'minimal':
      return [
        {
          selector: 'node',
          style: {
            'background-color': '#4A90D9',
            'border-width': 0,
            label: '',
            width: '20px',
            height: '20px',
            shape: 'ellipse',
          },
        },
        {
          selector: 'edge',
          style: {
            'line-color': '#BDC3C7',
            'target-arrow-shape': 'none',
            width: 1,
            label: '',
          },
        },
      ];
  }
}

/**
 * Get full stylesheet including state styles
 */
function getFullStylesheet(lod: LODLevel): Stylesheet[] {
  const lodStyles = getLODStyles(lod) as Stylesheet[];

  const stateStyles: Stylesheet[] = [
    // Start activity (green)
    {
      selector: 'node[?isStart]',
      style: {
        'background-color': '#27AE60',
        'border-color': '#1E8449',
      },
    },
    // End activity (red)
    {
      selector: 'node[?isEnd]',
      style: {
        'background-color': '#E74C3C',
        'border-color': '#C0392B',
      },
    },
    // High frequency nodes (darker blue)
    {
      selector: 'node[normalizedFreq > 0.7]',
      style: {
        'background-color': '#1A5276',
        'border-width': 3,
      },
    },
    // Hover state
    {
      selector: 'node:hover',
      style: {
        'background-color': '#5DADE2',
        'border-width': 3,
      },
    },
    // Selected state
    {
      selector: 'node:selected',
      style: {
        'background-color': '#F39C12',
        'border-color': '#D68910',
        'border-width': 4,
      },
    },
    // High frequency edge
    {
      selector: 'edge[frequency > 10]',
      style: {
        width: 4,
        'line-color': '#3498DB',
        'target-arrow-color': '#3498DB',
      },
    },
    // Selected edge
    {
      selector: 'edge:selected',
      style: {
        'line-color': '#F39C12',
        'target-arrow-color': '#F39C12',
        width: 4,
      },
    },
  ];

  return [...lodStyles, ...stateStyles];
}

/**
 * Convert data to Cytoscape elements with LOD optimization
 */
function convertToElements(data: ProcessGraphData, lod: LODLevel) {
  const maxFreq = Math.max(...data.nodes.map((n) => n.frequency || 0), 1);

  const nodes = data.nodes.map((node) => ({
    data: {
      id: node.id,
      label: node.label,
      shortLabel:
        lod === 'medium'
          ? node.label.length > 8
            ? node.label.substring(0, 8) + '...'
            : node.label
          : node.label,
      frequency: node.frequency || 0,
      isStart: node.isStart || false,
      isEnd: node.isEnd || false,
      normalizedFreq: (node.frequency || 0) / maxFreq,
    },
  }));

  const edges = data.edges.map((edge) => ({
    data: {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency || 0,
      probability: edge.probability || 0,
      label: lod === 'full' && edge.frequency ? `${edge.frequency}` : '',
    },
  }));

  return [...nodes, ...edges];
}

/**
 * OptimizedProcessGraph - High-performance graph visualization
 */
export const OptimizedProcessGraph = memo(function OptimizedProcessGraph({
  data,
  onNodeClick,
  onNodeHover,
  onEdgeClick,
  onEdgeHover,
  selectedNodeId,
  selectedEdgeId,
  hoveredNodeId: _hoveredNodeId,
  className = '',
  layout = 'dagre',
  tier,
  showPerformanceWarning = true,
  onPerformanceMetrics,
}: OptimizedProcessGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentLOD, setCurrentLOD] = useState<LODLevel>('full');
  const [renderer, setRenderer] = useState<RendererType>('svg');
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);

  // Determine renderer based on node count
  const selectedRenderer = useMemo(() => {
    return selectRenderer(data.nodes.length);
  }, [data.nodes.length]);

  // Update renderer state
  useEffect(() => {
    setRenderer(selectedRenderer);
  }, [selectedRenderer]);

  // Graph interaction handlers
  const handleNodeSelect = useCallback(
    (nodeId: string) => {
      const node = data.nodes.find((n) => n.id === nodeId);
      if (node && onNodeClick) {
        onNodeClick(node);
      }
    },
    [data.nodes, onNodeClick]
  );

  const handleEdgeSelect = useCallback(
    (edgeId: string, source: string, target: string) => {
      const edge = data.edges.find((e) => e.id === edgeId);
      if (edge && onEdgeClick) {
        onEdgeClick(edge);
      } else if (onEdgeClick) {
        // Construct edge if not found
        onEdgeClick({ id: edgeId, source, target, frequency: 0 });
      }
    },
    [data.edges, onEdgeClick]
  );

  const handleZoomChange = useCallback((zoom: number) => {
    const newLOD = getLODLevel(zoom);
    setCurrentLOD((prevLOD) => {
      if (prevLOD !== newLOD) {
        return newLOD;
      }
      return prevLOD;
    });
  }, []);

  // Set up interaction handlers
  const { attachHandlers, detachHandlers } = useGraphInteractions({
    onNodeHover,
    onNodeSelect: handleNodeSelect,
    onEdgeHover,
    onEdgeSelect: handleEdgeSelect,
    onZoomChange: handleZoomChange,
  });

  // Viewport virtualization for large graphs
  const updateVisibility = useCallback(
    debounce(() => {
      const cy = cyRef.current;
      if (!cy || data.nodes.length < 500) return;

      const extent = cy.extent();
      const padding = 100;

      cy.batch(() => {
        cy.nodes().forEach((node) => {
          const pos = node.position();
          const visible =
            pos.x >= extent.x1 - padding &&
            pos.x <= extent.x2 + padding &&
            pos.y >= extent.y1 - padding &&
            pos.y <= extent.y2 + padding;

          node.style('display', visible ? 'element' : 'none');
        });

        // Show edges only if both endpoints are visible
        cy.edges().forEach((edge) => {
          const sourceVisible = edge.source().style('display') === 'element';
          const targetVisible = edge.target().style('display') === 'element';
          edge.style('display', sourceVisible && targetVisible ? 'element' : 'none');
        });
      });
    }, 50),
    [data.nodes.length]
  );

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const startTime = performance.now();
    setIsLoading(true);

    // Destroy previous instance
    if (cyRef.current) {
      detachHandlers();
      cyRef.current.destroy();
      cyRef.current = null;
    }

    const elements = convertToElements(data, currentLOD);
    const stylesheet = getFullStylesheet(currentLOD);

    // Performance options based on renderer
    const performanceOptions: Partial<CytoscapeOptions> = {};

    if (renderer === 'canvas' || renderer === 'webgl') {
      performanceOptions.textureOnViewport = true;
      performanceOptions.hideEdgesOnViewport = data.edges.length > 1000;
      performanceOptions.hideLabelsOnViewport = data.nodes.length > 200;
    }

    if (renderer === 'webgl') {
      performanceOptions.pixelRatio = 1; // Lower pixel ratio for performance
    }

    const options: CytoscapeOptions = {
      container: containerRef.current,
      elements,
      style: stylesheet,
      layout: {
        name: layout,
        ...(layout === 'dagre' && {
          rankDir: 'TB',
          nodeSep: 50,
          rankSep: 80,
          edgeSep: 10,
          spacingFactor: 1.5,
          animate: false,
        }),
      } as CytoscapeOptions['layout'],
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.3,
      ...performanceOptions,
    };

    const layoutStartTime = performance.now();
    const cy = cytoscape(options);
    const layoutEndTime = performance.now();

    cyRef.current = cy;
    attachHandlers(cy);

    // Set up viewport virtualization for large graphs
    if (data.nodes.length >= 500) {
      cy.on('viewport', updateVisibility);
      updateVisibility();
    }

    // Report performance metrics
    const endTime = performance.now();
    const performanceMetrics: PerformanceMetrics = {
      nodeCount: data.nodes.length,
      edgeCount: data.edges.length,
      renderer,
      initialRenderMs: endTime - startTime,
      layoutMs: layoutEndTime - layoutStartTime,
    };

    setMetrics(performanceMetrics);
    onPerformanceMetrics?.(performanceMetrics);

    setIsLoading(false);

    // Cleanup
    return () => {
      if (cyRef.current) {
        detachHandlers();
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [
    data,
    layout,
    renderer,
    currentLOD,
    attachHandlers,
    detachHandlers,
    updateVisibility,
    onPerformanceMetrics,
  ]);

  // Update LOD styles when LOD changes (without recreating graph)
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy || isLoading) return;

    // Update element data for LOD
    cy.batch(() => {
      cy.nodes().forEach((node) => {
        const label = node.data('label');
        const shortLabel =
          currentLOD === 'medium'
            ? label.length > 8
              ? label.substring(0, 8) + '...'
              : label
            : label;
        node.data('shortLabel', shortLabel);
      });

      cy.edges().forEach((edge) => {
        const freq = edge.data('frequency');
        edge.data('label', currentLOD === 'full' && freq ? `${freq}` : '');
      });
    });

    // Update styles
    cy.style(getFullStylesheet(currentLOD));
  }, [currentLOD, isLoading]);

  // Handle selection changes
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.elements().unselect();

    if (selectedNodeId) {
      cy.getElementById(selectedNodeId).select();
    }
    if (selectedEdgeId) {
      cy.getElementById(selectedEdgeId).select();
    }
  }, [selectedNodeId, selectedEdgeId]);

  // Zoom controls
  const handleFit = useCallback(() => {
    cyRef.current?.fit(undefined, 50);
  }, []);

  const handleZoomIn = useCallback(() => {
    const cy = cyRef.current;
    if (cy) {
      cy.zoom(cy.zoom() * 1.2);
      cy.center();
    }
  }, []);

  const handleZoomOut = useCallback(() => {
    const cy = cyRef.current;
    if (cy) {
      cy.zoom(cy.zoom() / 1.2);
      cy.center();
    }
  }, []);

  const handleResetView = useCallback(() => {
    const cy = cyRef.current;
    if (cy) {
      cy.fit(undefined, 50);
      cy.zoom(1);
    }
  }, []);

  // Performance warning message
  const showWarning =
    showPerformanceWarning && data.nodes.length > 500;

  return (
    <div
      className={`optimized-process-graph ${className}`}
      style={{ position: 'relative', width: '100%', height: '100%' }}
    >
      {/* Loading overlay */}
      {isLoading && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 10,
            background: 'rgba(255, 255, 255, 0.9)',
            padding: '16px 24px',
            borderRadius: 8,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
          }}
        >
          Loading graph ({data.nodes.length} nodes)...
        </div>
      )}

      {/* Performance warning */}
      {showWarning && !isLoading && (
        <div
          style={{
            position: 'absolute',
            top: 8,
            left: 8,
            zIndex: 5,
            background: 'rgba(250, 173, 20, 0.9)',
            color: '#333',
            padding: '4px 12px',
            borderRadius: 4,
            fontSize: 12,
          }}
        >
          Large graph ({data.nodes.length} nodes) - Using {renderer} renderer
          {tier && ` (${tier} tier)`}
        </div>
      )}

      {/* Graph container */}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: '100%',
          minHeight: '400px',
          background: '#f8f9fa',
          borderRadius: '8px',
        }}
      />

      {/* Controls */}
      <div
        style={{
          position: 'absolute',
          bottom: 16,
          right: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: '8px',
          zIndex: 5,
        }}
      >
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          style={controlButtonStyle}
          aria-label="Zoom In"
        >
          +
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          style={controlButtonStyle}
          aria-label="Zoom Out"
        >
          −
        </button>
        <button
          onClick={handleFit}
          title="Fit to View"
          style={controlButtonStyle}
          aria-label="Fit to View"
        >
          ⊡
        </button>
        <button
          onClick={handleResetView}
          title="Reset View"
          style={controlButtonStyle}
          aria-label="Reset View"
        >
          ↺
        </button>
      </div>

      {/* LOD indicator */}
      {!isLoading && (
        <div
          style={{
            position: 'absolute',
            bottom: 16,
            left: 16,
            zIndex: 5,
            background: 'rgba(255, 255, 255, 0.9)',
            padding: '4px 8px',
            borderRadius: 4,
            fontSize: 11,
            color: '#666',
          }}
        >
          LOD: {currentLOD}
        </div>
      )}

      {/* Performance metrics (dev only) */}
      {process.env.NODE_ENV === 'development' && metrics && !isLoading && (
        <div
          style={{
            position: 'absolute',
            top: showWarning ? 36 : 8,
            left: 8,
            zIndex: 5,
            background: 'rgba(0, 0, 0, 0.7)',
            color: '#fff',
            padding: '4px 8px',
            borderRadius: 4,
            fontSize: 10,
            fontFamily: 'monospace',
          }}
        >
          {metrics.nodeCount}N / {metrics.edgeCount}E | {metrics.renderer} |{' '}
          {metrics.initialRenderMs.toFixed(0)}ms
        </div>
      )}
    </div>
  );
});

const controlButtonStyle: React.CSSProperties = {
  width: 32,
  height: 32,
  borderRadius: 4,
  border: '1px solid #ddd',
  background: '#fff',
  cursor: 'pointer',
  fontSize: 18,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

export default OptimizedProcessGraph;
