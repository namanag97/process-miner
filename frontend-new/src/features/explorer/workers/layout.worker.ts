/**
 * ELK Layout Web Worker
 * 
 * Performs graph layout computation off the main thread using ELK.js.
 * This prevents UI freezing when laying out large process graphs.
 */

import ELK, { ElkNode, ElkExtendedEdge, LayoutOptions } from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

export interface LayoutMessage {
    nodes: GraphNode[];
    edges: GraphEdge[];
    options?: LayoutOptions;
}

export interface GraphNode {
    id: string;
    label: string;
    width?: number;
    height?: number;
}

export interface GraphEdge {
    id: string;
    source: string;
    target: string;
}

export interface LayoutResult {
    nodes: Array<{ id: string; x: number; y: number; width: number; height: number }>;
    edges: Array<{ id: string; sections?: any[] }>;
}

/**
 * Build ELK graph structure from nodes and edges
 */
function buildElkGraph(nodes: GraphNode[], edges: GraphEdge[]): ElkNode {
    return {
        id: 'root',
        layoutOptions: {
            'elk.algorithm': 'layered',
            'elk.direction': 'RIGHT',
            'elk.spacing.nodeNode': '50',
            'elk.layered.spacing.nodeNodeBetweenLayers': '100',
            'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
        },
        children: nodes.map(node => ({
            id: node.id,
            width: node.width || 150,
            height: node.height || 50,
            labels: [{ text: node.label }],
        })),
        edges: edges.map(edge => ({
            id: edge.id,
            sources: [edge.source],
            targets: [edge.target],
        })) as ElkExtendedEdge[],
    };
}

/**
 * Worker message handler
 */
self.onmessage = async (event: MessageEvent<LayoutMessage>) => {
    const { nodes, edges, options } = event.data;

    try {
        const elkGraph = buildElkGraph(nodes, edges);

        // Merge custom options if provided
        if (options) {
            elkGraph.layoutOptions = { ...elkGraph.layoutOptions, ...options };
        }

        const layoutedGraph = await elk.layout(elkGraph);

        const result: LayoutResult = {
            nodes: (layoutedGraph.children || []).map(child => ({
                id: child.id,
                x: child.x || 0,
                y: child.y || 0,
                width: child.width || 150,
                height: child.height || 50,
            })),
            edges: (layoutedGraph.edges || []).map(edge => ({
                id: edge.id,
                sections: edge.sections,
            })),
        };

        self.postMessage({ success: true, result });
    } catch (error) {
        self.postMessage({
            success: false,
            error: error instanceof Error ? error.message : 'Layout failed',
        });
    }
};

export { };
