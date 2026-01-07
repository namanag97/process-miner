/**
 * GraphViewer Component
 * 
 * Interactive graph visualization using Cytoscape.js.
 * Handles Petri Nets, Transition Systems, Prefix Trees as node/edge graphs.
 */

import { useEffect, useRef, useCallback, useMemo } from 'react';
import cytoscape, { Core, CytoscapeOptions } from 'cytoscape';
import styles from './GraphViewer.module.css';

export interface GraphNode {
    id: string;
    label: string;
    type?: 'place' | 'transition' | 'state' | 'activity';
    isStart?: boolean;
    isEnd?: boolean;
    tokens?: number;
}

export interface GraphEdge {
    source: string;
    target: string;
    label?: string;
    weight?: number;
}

export interface GraphViewerProps {
    nodes: GraphNode[];
    edges: GraphEdge[];
    title?: string;
    layoutDirection?: 'TB' | 'LR';
}

/**
 * Get Cytoscape stylesheet for different node types
 */
function getGraphViewerStyle(): cytoscape.StylesheetStyle[] {
    return [
        // Default node style
        {
            selector: 'node',
            style: {
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'background-color': '#6366f1',
                'color': '#fff',
                'font-size': '12px',
                'width': '100px',
                'height': '40px',
                'shape': 'roundrectangle',
                'text-wrap': 'ellipsis',
                'text-max-width': '90px',
                'border-width': 2,
                'border-color': '#4f46e5',
            },
        },
        // Petri Net places (circles)
        {
            selector: 'node[nodeType = "place"]',
            style: {
                'width': '40px',
                'height': '40px',
                'shape': 'ellipse',
                'background-color': '#1e1e2e',
                'border-width': 2,
                'border-color': '#6366f1',
                'label': 'data(tokens)',
                'color': '#fff',
                'font-size': '14px',
            },
        },
        // Petri Net transitions (rectangles)
        {
            selector: 'node[nodeType = "transition"]',
            style: {
                'width': '12px',
                'height': '40px',
                'shape': 'rectangle',
                'background-color': '#10b981',
                'border-width': 0,
                'label': '',
            },
        },
        // Start nodes
        {
            selector: 'node[?isStart]',
            style: {
                'border-width': 3,
                'border-color': '#10b981',
            },
        },
        // End nodes
        {
            selector: 'node[?isEnd]',
            style: {
                'border-width': 3,
                'border-color': '#ef4444',
            },
        },
        // Edge style
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#6366f1',
                'target-arrow-color': '#6366f1',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'label': 'data(label)',
                'font-size': '10px',
                'color': '#888',
                'text-background-color': '#1e1e2e',
                'text-background-opacity': 0.9,
                'text-background-padding': '2px',
            },
        },
    ];
}

export function GraphViewer({
    nodes: graphNodes,
    edges: graphEdges,
    title,
    layoutDirection = 'LR'
}: GraphViewerProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const cyRef = useRef<Core | null>(null);

    // Convert to Cytoscape elements
    const elements = useMemo(() => {
        const nodes = graphNodes.map((node: any) => ({
            data: {
                id: node.id,
                label: node.type === 'transition' ? '' : node.label,
                nodeType: node.type || 'activity',
                isStart: node.isStart || false,
                isEnd: node.isEnd || false,
                tokens: node.tokens !== undefined ? String(node.tokens) : '',
            },
        }));

        const edges = graphEdges.map((edge, index) => ({
            data: {
                id: `e-${edge.source}-${edge.target}-${index}`,
                source: edge.source,
                target: edge.target,
                label: edge.label || (edge.weight !== undefined ? String(edge.weight) : ''),
            },
        }));

        return [...nodes, ...edges];
    }, [graphNodes, graphEdges]);

    // Initialize Cytoscape
    useEffect(() => {
        if (!containerRef.current || graphNodes.length === 0) return;

        const options: CytoscapeOptions = {
            container: containerRef.current,
            elements,
            style: getGraphViewerStyle(),
            layout: {
                name: 'breadthfirst',
                directed: true,
                spacingFactor: 1.5,
                animate: false,
            },
            minZoom: 0.1,
            maxZoom: 2,
            wheelSensitivity: 0.3,
        };

        cyRef.current = cytoscape(options);

        // Fit to viewport after layout
        setTimeout(() => {
            cyRef.current?.fit(undefined, 40);
        }, 100);

        return () => {
            cyRef.current?.destroy();
            cyRef.current = null;
        };
    }, [elements, layoutDirection, graphNodes.length]);

    // Zoom controls
    const handleZoomIn = useCallback(() => {
        const cy = cyRef.current;
        if (cy) cy.zoom(cy.zoom() * 1.2);
    }, []);

    const handleZoomOut = useCallback(() => {
        const cy = cyRef.current;
        if (cy) cy.zoom(cy.zoom() / 1.2);
    }, []);

    const handleFit = useCallback(() => {
        cyRef.current?.fit(undefined, 40);
    }, []);

    if (graphNodes.length === 0) {
        return (
            <div className={styles.container}>
                <div className={styles.empty}>No graph data available</div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            {title && <div className={styles.title}>{title}</div>}
            <div className={styles.canvas}>
                <div
                    ref={containerRef}
                    style={{ width: '100%', height: '100%', minHeight: '300px' }}
                />
                {/* Zoom controls */}
                <div style={{
                    position: 'absolute',
                    bottom: 16,
                    right: 16,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                    zIndex: 5,
                }}>
                    <button onClick={handleZoomIn} title="Zoom In" style={controlStyle}>+</button>
                    <button onClick={handleZoomOut} title="Zoom Out" style={controlStyle}>−</button>
                    <button onClick={handleFit} title="Fit to View" style={controlStyle}>⊡</button>
                </div>
            </div>
        </div>
    );
}

const controlStyle: React.CSSProperties = {
    width: 28,
    height: 28,
    borderRadius: 4,
    border: '1px solid #333',
    background: '#1e1e2e',
    color: '#fff',
    cursor: 'pointer',
    fontSize: 16,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
};

export default GraphViewer;
