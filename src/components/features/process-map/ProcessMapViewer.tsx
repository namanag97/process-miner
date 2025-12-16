'use client';

import { useCallback, useState, useMemo } from 'react';
import {
    ReactFlow,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
    type NodeMouseHandler,
    type EdgeMouseHandler,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import type { ProcessModel } from '@/lib/mining/types';
import { useProcessMapFlow } from './useProcessMapFlow';
import { ActivityNode } from './nodes/ActivityNode';
import { ProcessEdge } from './edges/ProcessEdge';
import { ProcessMapLegend } from './ProcessMapLegend';
import { NodeDetailPanel } from './NodeDetailPanel';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('process-map-viewer');

interface ProcessMapViewerProps {
    model: ProcessModel;
}

// Define custom node types - use type assertion for ReactFlow compatibility
const nodeTypes = {
    activityNode: ActivityNode,
} as const;

// Define custom edge types - use type assertion for ReactFlow compatibility
const edgeTypes = {
    processEdge: ProcessEdge,
} as const;

export function ProcessMapViewer({ model }: ProcessMapViewerProps) {
    const { nodes: initialNodes, edges: initialEdges } = useProcessMapFlow(model);

    // Cast to any to avoid ReactFlow v12 strict typing issues with custom data
    const [nodes, , onNodesChange] = useNodesState(initialNodes as any);
    const [edges, , onEdgesChange] = useEdgesState(initialEdges as any);

    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

    // Handle node click
    const onNodeClick: NodeMouseHandler = useCallback((_event, node) => {
        logger.info(`Node clicked: ${node.id}`);
        setSelectedNodeId(node.id);
        setSelectedEdgeId(null);
    }, []);

    // Handle edge click
    const onEdgeClick: EdgeMouseHandler = useCallback((_event, edge) => {
        logger.info(`Edge clicked: ${edge.id}`);
        setSelectedEdgeId(edge.id);
        setSelectedNodeId(null);
    }, []);

    // Handle pane click (deselect)
    const onPaneClick = useCallback(() => {
        setSelectedNodeId(null);
        setSelectedEdgeId(null);
    }, []);

    // Close detail panel
    const handleClosePanel = useCallback(() => {
        setSelectedNodeId(null);
        setSelectedEdgeId(null);
    }, []);

    // Arrow marker definition
    const arrowMarker = useMemo(
        () => (
            <svg>
                <defs>
                    <marker
                        id="arrow"
                        viewBox="0 0 10 10"
                        refX="8"
                        refY="5"
                        markerWidth="6"
                        markerHeight="6"
                        orient="auto-start-reverse"
                    >
                        <path
                            d="M 0 0 L 10 5 L 0 10 z"
                            fill="hsl(var(--muted-foreground))"
                        />
                    </marker>
                </defs>
            </svg>
        ),
        []
    );

    return (
        <div className="w-full h-[600px] relative border rounded-lg bg-background">
            {/* Arrow marker SVG (hidden but defines the marker) */}
            <div className="hidden">{arrowMarker}</div>

            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={onNodeClick}
                onEdgeClick={onEdgeClick}
                onPaneClick={onPaneClick}
                nodeTypes={nodeTypes as any}
                edgeTypes={edgeTypes as any}
                fitView
                fitViewOptions={{ padding: 0.2 }}
                minZoom={0.1}
                maxZoom={2}
                defaultEdgeOptions={{
                    type: 'processEdge',
                }}
            >
                <Background />
                <Controls position="bottom-left" />
                <MiniMap
                    position="bottom-right"
                    nodeColor={(node) => {
                        if (node.data?.isStart) return '#22c55e';
                        if (node.data?.isEnd) return '#ef4444';
                        return '#6b7280';
                    }}
                    maskColor="rgba(0, 0, 0, 0.1)"
                />
            </ReactFlow>

            {/* Legend */}
            <ProcessMapLegend />

            {/* Detail Panel */}
            <NodeDetailPanel
                model={model}
                selectedNodeId={selectedNodeId}
                selectedEdgeId={selectedEdgeId}
                onClose={handleClosePanel}
            />

            {/* CSS for animated dashed edges */}
            <style jsx global>{`
                @keyframes dashmove {
                    0% {
                        stroke-dashoffset: 10;
                    }
                    100% {
                        stroke-dashoffset: 0;
                    }
                }
            `}</style>
        </div>
    );
}
