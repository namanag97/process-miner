import React, { useMemo, useCallback, useState } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  MiniMap,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Card, Spin, Alert, Empty, Space, Segmented, Tooltip } from 'antd';
import { useDFG } from '../hooks';
import { ActivityNode } from './ActivityNode';
import { TransitionEdge } from './TransitionEdge';
import type { DFGNode, DFGEdge } from 'process-mining-sdk';

// Custom node types
const nodeTypes = {
  activity: ActivityNode,
};

// Custom edge types
const edgeTypes = {
  transition: TransitionEdge,
};

export type ColorMode = 'frequency' | 'performance';

interface ProcessMapProps {
  logId: string;
  onNodeClick?: (nodeId: string, data: DFGNode) => void;
  onEdgeClick?: (edge: DFGEdge) => void;
  colorMode?: ColorMode;
  selectedActivities?: string[];
  style?: React.CSSProperties;
}

// Dagre-like layout algorithm
function layoutGraph(
  dfgNodes: DFGNode[],
  dfgEdges: DFGEdge[],
  startActivities: Record<string, number>,
  endActivities: Record<string, number>
): { nodes: Node[]; edges: Edge[] } {
  // Build adjacency and calculate levels
  const nodeMap = new Map(dfgNodes.map((n) => [n.id, n]));
  const incomingEdges = new Map<string, string[]>();
  const outgoingEdges = new Map<string, string[]>();

  dfgEdges.forEach((edge) => {
    if (!incomingEdges.has(edge.target)) incomingEdges.set(edge.target, []);
    if (!outgoingEdges.has(edge.source)) outgoingEdges.set(edge.source, []);
    incomingEdges.get(edge.target)!.push(edge.source);
    outgoingEdges.get(edge.source)!.push(edge.target);
  });

  // Find start nodes (no incoming edges or explicit start activities)
  const startNodes = dfgNodes.filter(
    (n) =>
      !incomingEdges.has(n.id) ||
      incomingEdges.get(n.id)!.length === 0 ||
      startActivities[n.label]
  );

  // Calculate levels using BFS
  const levels = new Map<string, number>();
  const queue: string[] = startNodes.map((n) => n.id);
  startNodes.forEach((n) => levels.set(n.id, 0));

  while (queue.length > 0) {
    const nodeId = queue.shift()!;
    const level = levels.get(nodeId) || 0;
    const targets = outgoingEdges.get(nodeId) || [];

    targets.forEach((targetId) => {
      const currentLevel = levels.get(targetId);
      if (currentLevel === undefined || currentLevel < level + 1) {
        levels.set(targetId, level + 1);
        if (!queue.includes(targetId)) {
          queue.push(targetId);
        }
      }
    });
  }

  // Assign levels to remaining nodes
  dfgNodes.forEach((n) => {
    if (!levels.has(n.id)) {
      levels.set(n.id, 0);
    }
  });

  // Group nodes by level
  const levelGroups = new Map<number, DFGNode[]>();
  dfgNodes.forEach((n) => {
    const level = levels.get(n.id) || 0;
    if (!levelGroups.has(level)) levelGroups.set(level, []);
    levelGroups.get(level)!.push(n);
  });

  // Calculate positions
  const NODE_WIDTH = 180;
  const NODE_HEIGHT = 60;
  const HORIZONTAL_GAP = 100;
  const VERTICAL_GAP = 80;

  const maxFrequency = Math.max(...dfgNodes.map((n) => n.frequency), 1);

  const nodes: Node[] = [];
  const sortedLevels = Array.from(levelGroups.keys()).sort((a, b) => a - b);

  sortedLevels.forEach((level) => {
    const nodesAtLevel = levelGroups.get(level) || [];
    // Sort by frequency descending
    nodesAtLevel.sort((a, b) => b.frequency - a.frequency);

    const levelWidth = nodesAtLevel.length * (NODE_WIDTH + HORIZONTAL_GAP);
    const startX = -(levelWidth / 2) + NODE_WIDTH / 2;

    nodesAtLevel.forEach((dfgNode, index) => {
      const isStart = !!startActivities[dfgNode.label];
      const isEnd = !!endActivities[dfgNode.label];

      nodes.push({
        id: dfgNode.id,
        type: 'activity',
        position: {
          x: startX + index * (NODE_WIDTH + HORIZONTAL_GAP),
          y: level * (NODE_HEIGHT + VERTICAL_GAP),
        },
        data: {
          label: dfgNode.label,
          frequency: dfgNode.frequency,
          maxFrequency,
          isStart,
          isEnd,
        },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      });
    });
  });

  // Create edges
  const maxEdgeFrequency = Math.max(...dfgEdges.map((e) => e.frequency), 1);

  const edges: Edge[] = dfgEdges.map((dfgEdge) => ({
    id: `${dfgEdge.source}-${dfgEdge.target}`,
    source: dfgEdge.source,
    target: dfgEdge.target,
    type: 'transition',
    animated: dfgEdge.frequency / maxEdgeFrequency > 0.5,
    data: {
      frequency: dfgEdge.frequency,
      maxFrequency: maxEdgeFrequency,
      performance: dfgEdge.performance,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 15,
      height: 15,
    },
  }));

  return { nodes, edges };
}

export const ProcessMap: React.FC<ProcessMapProps> = ({
  logId,
  onNodeClick,
  onEdgeClick,
  colorMode = 'frequency',
  selectedActivities,
  style,
}) => {
  const { data: dfgData, isLoading, error } = useDFG(logId);
  const [internalColorMode, setInternalColorMode] = useState<ColorMode>(colorMode);

  const { initialNodes, initialEdges } = useMemo(() => {
    if (!dfgData) {
      return { initialNodes: [], initialEdges: [] };
    }

    const { nodes, edges } = layoutGraph(
      dfgData.nodes,
      dfgData.edges,
      dfgData.start_activities,
      dfgData.end_activities
    );

    // Apply color mode and selection styling
    const styledNodes = nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        colorMode: internalColorMode,
        isSelected: selectedActivities?.includes(node.data.label as string),
      },
    }));

    const styledEdges = edges.map((edge) => ({
      ...edge,
      data: {
        ...edge.data,
        colorMode: internalColorMode,
      },
    }));

    return { initialNodes: styledNodes, initialEdges: styledEdges };
  }, [dfgData, internalColorMode, selectedActivities]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when data changes
  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick && dfgData) {
        const dfgNode = dfgData.nodes.find((n) => n.id === node.id);
        if (dfgNode) {
          onNodeClick(node.id, dfgNode);
        }
      }
    },
    [onNodeClick, dfgData]
  );

  const handleEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      if (onEdgeClick && dfgData) {
        const dfgEdge = dfgData.edges.find(
          (e) => e.source === edge.source && e.target === edge.target
        );
        if (dfgEdge) {
          onEdgeClick(dfgEdge);
        }
      }
    },
    [onEdgeClick, dfgData]
  );

  if (isLoading) {
    return (
      <Card style={{ height: 500, display: 'flex', alignItems: 'center', justifyContent: 'center', ...style }}>
        <Spin size="large" tip="Loading process model..." />
      </Card>
    );
  }

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load process model"
        description="Could not retrieve the process visualization for this log."
      />
    );
  }

  if (!dfgData || dfgData.nodes.length === 0) {
    return (
      <Card style={{ height: 500, ...style }}>
        <Empty description="No process data available" />
      </Card>
    );
  }

  return (
    <div style={{ height: 500, ...style }}>
      <div style={{ marginBottom: 8, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Space>
          <Segmented
            size="small"
            value={internalColorMode}
            onChange={(value) => setInternalColorMode(value as ColorMode)}
            options={[
              { label: 'Frequency', value: 'frequency' },
              { label: 'Performance', value: 'performance' },
            ]}
          />
        </Space>
        <span style={{ fontSize: 12, color: '#666' }}>
          {dfgData.nodes.length} activities, {dfgData.edges.length} transitions, {dfgData.total_cases} cases
        </span>
      </div>
      <div style={{ height: 'calc(100% - 40px)', border: '1px solid #d9d9d9', borderRadius: 4 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={handleNodeClick}
          onEdgeClick={handleEdgeClick}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          fitView
          minZoom={0.1}
          maxZoom={2}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
        >
          <Controls />
          <MiniMap
            nodeStrokeColor="#0052cc"
            nodeColor={(node) => (node.data?.isSelected ? '#0052cc' : '#e6f0ff')}
            nodeBorderRadius={4}
          />
          <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        </ReactFlow>
      </div>
    </div>
  );
};
