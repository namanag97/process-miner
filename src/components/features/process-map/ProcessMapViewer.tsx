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

import { ActivityNode } from './nodes/ActivityNode';
import { ProcessEdge } from './edges/ProcessEdge';
import { ProcessMapLegend } from './ProcessMapLegend';
import { NodeDetailPanel } from './NodeDetailPanel';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('process-map-viewer');

interface ProcessMapViewerProps {
    dfg: {
        nodes: any[];
        edges: any[];
        summary?: any;
    };
}

// Define custom node types - use type assertion for ReactFlow compatibility
const nodeTypes = {
    activityNode: ActivityNode,
} as const;

// Define custom edge types - use type assertion for ReactFlow compatibility
const edgeTypes = {
    processEdge: ProcessEdge,
} as const;

export function ProcessMapViewer({ dfg }: ProcessMapViewerProps) {
    // Use DFG nodes and edges directly from backend (already in ReactFlow format)
    const initialNodes = dfg?.nodes || [];
    const initialEdges = dfg?.edges || [];

    // Cast to any to avoid ReactFlow v12 strict typing issues with custom data
    const [nodes, , onNodesChange] = useNodesState(initialNodes as any);
    const [edges, , onEdgesChange] = useEdgesState(initialEdges as any);

    const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
    const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

    // Transform DFG nodes to activity format for NodeDetailPanel
    const activities = useMemo(() => {
        return (dfg?.nodes || []).map((node: any) => ({
            name: node.data?.label || node.id,
            frequency: node.data?.frequency || 0,
            avgDuration: node.data?.avgDuration || 0,
            isStart: node.data?.isStart || false,
            isEnd: node.data?.isEnd || false,
        }));
    }, [dfg?.nodes]);

    // Transform DFG edges for NodeDetailPanel
    const dfgEdges = useMemo(() => {
        return (dfg?.edges || []).map((edge: any) => ({
            source: edge.source,
            target: edge.target,
            frequency: edge.data?.frequency || 0,
            avgDuration: edge.data?.avgDuration || 0,
            cases: [], // DFG response doesn't include case IDs
        }));
    }, [dfg?.edges]);

    // Create a compatible model for NodeDetailPanel
    const panelModel = useMemo(() => ({
        activities,
        edges: dfgEdges,
        variants: [],
        deviations: [],
        stats: {
            totalCases: 0,
            totalEvents: 0,
            avgCaseDuration: 0,
            medianCaseDuration: 0,
            startActivities: [],
            endActivities: [],
        },
    }), [activities, dfgEdges]);

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
                model={panelModel as any}
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
