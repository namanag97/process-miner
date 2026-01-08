/**
 * CytoscapeCanvas Component
 * 
 * Modern graph visualization using Cytoscape.js.
 * Replaces ReactFlow with a more performant, standards-compliant solution.
 */

import cytoscape, { Core, CytoscapeOptions } from 'cytoscape';
// @ts-expect-error - cytoscape-dagre has no types
import dagre from 'cytoscape-dagre';
import { useEffect, useRef, useCallback, useState } from 'react';

// BUG-004 FIX: Register dagre extension for proper hierarchical layouts
cytoscape.use(dagre);

// Types for process graph data
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
    startActivities?: Record<string, number>;
    endActivities?: Record<string, number>;
    totalFrequency?: number;
    metadata?: {
        nodeCount: number;
        edgeCount: number;
        type: string;
    };
}

export interface CytoscapeCanvasProps {
    data: ProcessGraphData;
    onNodeClick?: (node: ProcessNode) => void;
    onEdgeClick?: (edge: ProcessEdge) => void;
    className?: string;
    layout?: 'dagre' | 'preset' | 'cose';
    showLabels?: boolean;
    colorByFrequency?: boolean;
}

/**
 * Convert process graph data to Cytoscape elements format
 */
function convertToElements(data: ProcessGraphData) {
    const maxFreq = Math.max(...data.nodes.map(n => n.frequency || 0), 1);

    const nodes = data.nodes.map(node => ({
        data: {
            id: node.id,
            label: node.label,
            frequency: node.frequency || 0,
            isStart: node.isStart || false,
            isEnd: node.isEnd || false,
            // Normalize frequency for coloring
            normalizedFreq: (node.frequency || 0) / maxFreq,
        },
    }));

    const edges = data.edges.map(edge => ({
        data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            frequency: edge.frequency || 0,
            probability: edge.probability || 0,
            label: edge.frequency ? `${edge.frequency}` : '',
        },
    }));

    return [...nodes, ...edges];
}

/**
 * Get Cytoscape stylesheet for process graphs
 */
function getProcessGraphStyle(): cytoscape.StylesheetStyle[] {
    return [
        // Node base style
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#4A90D9',
                'color': '#ffffff',
                'font-size': '11px',
                'font-weight': 'bold',
                'width': '140px',
                'height': '45px',
                'shape': 'roundrectangle',
                'text-wrap': 'wrap',
                'text-max-width': '130px',
                'border-width': 2,
                'border-color': '#2E5A88',
                'text-outline-color': '#2E5A88',
                'text-outline-width': 1,
            },
        },
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
        // Edge base style
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#7F8C8D',
                'target-arrow-color': '#7F8C8D',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '10px',
                'text-background-color': '#fff',
                'text-background-opacity': 0.8,
                'text-background-padding': '2px',
            },
        },
        // High frequency edge
        {
            selector: 'edge[frequency > 10]',
            style: {
                'width': 4,
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
                'width': 4,
            },
        },
    ];
}

/**
 * CytoscapeCanvas - Modern process graph visualization component
 */
export function CytoscapeCanvas({
    data,
    onNodeClick,
    onEdgeClick,
    className = '',
    layout = 'dagre',
    showLabels: _showLabels = true,
    colorByFrequency: _colorByFrequency = true,
}: CytoscapeCanvasProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<Core | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize Cytoscape
    useEffect(() => {
        if (!containerRef.current) return;

        const elements = convertToElements(data);

        const options: CytoscapeOptions = {
            container: containerRef.current,
            elements,
            style: getProcessGraphStyle(),
            layout: {
                name: layout,  // BUG-004 FIX: dagre is now properly registered
                // Using type assertion for dagre-specific options (no types available)
                ...(layout === 'dagre' && {
                    rankDir: 'TB',  // Top to bottom
                    nodeSep: 50,
                    rankSep: 80,
                    edgeSep: 10,
                    spacingFactor: 1.5,
                    animate: false,
                }),
            } as CytoscapeOptions['layout'],
            minZoom: 0.2,
            maxZoom: 3,
            wheelSensitivity: 0.3,
        };

        cyRef.current = cytoscape(options);
        setIsLoading(false);

        // Event handlers
        if (onNodeClick) {
            cyRef.current.on('tap', 'node', (event) => {
                const node = event.target;
                onNodeClick({
                    id: node.id(),
                    label: node.data('label'),
                    frequency: node.data('frequency'),
                    isStart: node.data('isStart'),
                    isEnd: node.data('isEnd'),
                });
            });
        }

        if (onEdgeClick) {
            cyRef.current.on('tap', 'edge', (event) => {
                const edge = event.target;
                onEdgeClick({
                    id: edge.id(),
                    source: edge.source().id(),
                    target: edge.target().id(),
                    frequency: edge.data('frequency'),
                    probability: edge.data('probability'),
                });
            });
        }

        // Cleanup
        return () => {
            cyRef.current?.destroy();
        };
    }, [data, layout, onNodeClick, onEdgeClick]);

    // Fit to viewport
    const handleFit = useCallback(() => {
        cyRef.current?.fit(undefined, 50);
    }, []);

    // Zoom controls
    const handleZoomIn = useCallback(() => {
        const cy = cyRef.current;
        if (cy) {
            cy.zoom(cy.zoom() * 1.2);
        }
    }, []);

    const handleZoomOut = useCallback(() => {
        const cy = cyRef.current;
        if (cy) {
            cy.zoom(cy.zoom() / 1.2);
        }
    }, []);

    return (
        <div className={`cytoscape-canvas-wrapper ${className}`} style={{ position: 'relative', width: '100%', height: '100%' }}>
            {isLoading && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    zIndex: 10,
                }}>
                    Loading graph...
                </div>
            )}
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
            {/* Zoom controls */}
            <div style={{
                position: 'absolute',
                bottom: 16,
                right: 16,
                display: 'flex',
                flexDirection: 'column',
                gap: '8px',
                zIndex: 5,
            }}>
                <button onClick={handleZoomIn} title="Zoom In" style={controlButtonStyle}>+</button>
                <button onClick={handleZoomOut} title="Zoom Out" style={controlButtonStyle}>−</button>
                <button onClick={handleFit} title="Fit to View" style={controlButtonStyle}>⊡</button>
            </div>
        </div>
    );
}

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

export default CytoscapeCanvas;
