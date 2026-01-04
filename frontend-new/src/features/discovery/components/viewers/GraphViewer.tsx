/**
 * GraphViewer Component
 * 
 * Interactive graph visualization using React Flow.
 * Handles Petri Nets, Transition Systems, Prefix Trees as node/edge graphs.
 */

import { useCallback, useMemo } from 'react';
import ReactFlow, {
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    Node,
    Edge,
    MarkerType,
    ConnectionMode,
} from 'reactflow';
import 'reactflow/dist/style.css';
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

// Convert to React Flow format
function toReactFlowNodes(graphNodes: GraphNode[], direction: 'TB' | 'LR'): Node[] {
    const spacing = direction === 'TB' ? { x: 150, y: 100 } : { x: 200, y: 80 };

    return graphNodes.map((node, index) => {
        // Simple grid layout - will be improved with dagre
        const row = Math.floor(index / 5);
        const col = index % 5;

        let nodeType = 'default';
        let style: React.CSSProperties = {
            padding: '10px 20px',
            borderRadius: '8px',
            fontSize: '12px',
            fontWeight: 500,
        };

        // Petri Net places (circles)
        if (node.type === 'place') {
            style = {
                ...style,
                width: 40,
                height: 40,
                borderRadius: '50%',
                padding: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: '#1e1e2e',
                border: '2px solid #6366f1',
            };
        }

        // Petri Net transitions (rectangles)
        if (node.type === 'transition') {
            style = {
                ...style,
                width: 12,
                height: 40,
                borderRadius: '2px',
                padding: 0,
                background: '#10b981',
                border: 'none',
            };
        }

        // Start/End styling
        if (node.isStart) {
            style = { ...style, border: '3px solid #10b981' };
        }
        if (node.isEnd) {
            style = { ...style, border: '3px solid #ef4444' };
        }

        return {
            id: node.id,
            position: { x: col * spacing.x, y: row * spacing.y },
            data: {
                label: node.type === 'transition' ? '' : node.label,
                tokens: node.tokens,
            },
            style,
            type: nodeType,
        };
    });
}

function toReactFlowEdges(graphEdges: GraphEdge[]): Edge[] {
    return graphEdges.map((edge, index) => ({
        id: `e-${edge.source}-${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        label: edge.label || (edge.weight ? String(edge.weight) : undefined),
        markerEnd: { type: MarkerType.ArrowClosed },
        style: { stroke: '#6366f1' },
        labelStyle: { fill: '#888', fontSize: 10 },
    }));
}

export function GraphViewer({
    nodes: graphNodes,
    edges: graphEdges,
    title,
    layoutDirection = 'LR'
}: GraphViewerProps) {
    const initialNodes = useMemo(
        () => toReactFlowNodes(graphNodes, layoutDirection),
        [graphNodes, layoutDirection]
    );

    const initialEdges = useMemo(
        () => toReactFlowEdges(graphEdges),
        [graphEdges]
    );

    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

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
                <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    connectionMode={ConnectionMode.Loose}
                    fitView
                    fitViewOptions={{ padding: 0.2 }}
                    minZoom={0.1}
                    maxZoom={2}
                    proOptions={{ hideAttribution: true }}
                >
                    <Background color="#333" gap={16} />
                    <Controls />
                    <MiniMap
                        nodeColor="#6366f1"
                        maskColor="rgba(0,0,0,0.8)"
                        style={{ background: '#1e1e2e' }}
                    />
                </ReactFlow>
            </div>
        </div>
    );
}

export default GraphViewer;
