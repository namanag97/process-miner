import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  MarkerType,
  BackgroundVariant,
  Handle,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Typography } from 'antd';
import { tokens } from '@lumina/design-system';
import { DFGNode, DFGEdge, formatDuration } from '../mockExplorerData';
import { createLogger } from '../../../utils/logger';

const log = createLogger('ProcessCanvas');
const { Text } = Typography;

// =============================================================================
// CUSTOM NODE COMPONENT
// =============================================================================

interface ActivityNodeData {
  label: string;
  frequency: number;
  isStart?: boolean;
  isEnd?: boolean;
  isSelected?: boolean;
  isHighlighted?: boolean;
}

function ActivityNode({ data }: { data: ActivityNodeData }) {
  const backgroundColor = data.isStart
    ? tokens.colors.success[100]
    : data.isEnd
    ? tokens.colors.error[100]
    : data.isHighlighted
    ? tokens.colors.primary[100]
    : tokens.colors.neutral[0];

  const borderColor = data.isStart
    ? tokens.colors.success[500]
    : data.isEnd
    ? tokens.colors.error[500]
    : data.isHighlighted
    ? tokens.colors.primary[500]
    : data.isSelected
    ? tokens.colors.primary[500]
    : tokens.colors.neutral[300];

  return (
    <div
      style={{
        padding: '12px 16px',
        backgroundColor,
        border: `2px solid ${borderColor}`,
        borderRadius: tokens.radius.lg,
        minWidth: 120,
        textAlign: 'center',
        boxShadow: data.isSelected ? tokens.shadow.md : tokens.shadow.xs,
        position: 'relative',
      }}
    >
      {/* Target handle (input) on the left */}
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: tokens.colors.neutral[400],
          width: 8,
          height: 8,
        }}
      />
      
      <Text strong style={{ display: 'block', marginBottom: 4 }}>
        {data.label}
      </Text>
      <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
        {data.frequency.toLocaleString()} cases
      </Text>
      
      {/* Source handle (output) on the right */}
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: tokens.colors.neutral[400],
          width: 8,
          height: 8,
        }}
      />
    </div>
  );
}

const nodeTypes = {
  activity: ActivityNode,
};

// =============================================================================
// LAYOUT HELPERS
// =============================================================================

function layoutNodes(dfgNodes: DFGNode[], dfgEdges: DFGEdge[]): Node[] {
  // Simple horizontal layout based on topological sort
  // group nodes into layers based on dependencies
  const inDegree = new Map<string, number>();
  const adjacency = new Map<string, string[]>();

  dfgNodes.forEach((n) => {
    inDegree.set(n.id, 0);
    adjacency.set(n.id, []);
  });

  dfgEdges.forEach((e) => {
    inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
    adjacency.get(e.source)?.push(e.target);
  });

  // BFS to assign layers
  const layers = new Map<string, number>();
  const queue: string[] = [];

  dfgNodes.forEach((n) => {
    if ((inDegree.get(n.id) || 0) === 0) {
      queue.push(n.id);
      layers.set(n.id, 0);
    }
  });

  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentLayer = layers.get(current)!;
    const neighbors = adjacency.get(current) || [];

    neighbors.forEach((neighbor) => {
      const newLayer = currentLayer + 1;
      if (!layers.has(neighbor) || (layers.get(neighbor)! < newLayer)) {
        layers.set(neighbor, newLayer);
      }
      inDegree.set(neighbor, (inDegree.get(neighbor) || 1) - 1);
      if ((inDegree.get(neighbor) || 0) === 0) {
        queue.push(neighbor);
      }
    });
  }

  // Group nodes by layer
  const layerNodes = new Map<number, DFGNode[]>();
  dfgNodes.forEach((n) => {
    const layer = layers.get(n.id) || 0;
    if (!layerNodes.has(layer)) {
      layerNodes.set(layer, []);
    }
    layerNodes.get(layer)!.push(n);
  });

  // Create positioned nodes
  const nodes: Node[] = [];
  const horizontalSpacing = 200;
  const verticalSpacing = 100;

  layerNodes.forEach((nodesInLayer, layer) => {
    const yOffset = -(nodesInLayer.length - 1) * verticalSpacing / 2;
    nodesInLayer.forEach((n, index) => {
      const isStart = n.id === 'start' || n.label.toLowerCase().includes('start');
      const isEnd = n.id === 'end' || n.label.toLowerCase().includes('end');

      nodes.push({
        id: n.id,
        type: 'activity',
        position: {
          x: layer * horizontalSpacing,
          y: yOffset + index * verticalSpacing,
        },
        data: {
          label: n.label,
          frequency: n.frequency,
          isStart,
          isEnd,
        },
        sourcePosition: Position.Right,
        targetPosition: Position.Left,
      });
    });
  });

  return nodes;
}

function createEdges(dfgEdges: DFGEdge[]): Edge[] {
  return dfgEdges.map((e, index) => ({
    id: `e-${e.source}-${e.target}-${index}`,
    source: e.source,
    target: e.target,
    label: e.performance ? formatDuration(e.performance) : `${e.frequency}`,
    labelStyle: { fontSize: 11, fill: tokens.colors.neutral[600] },
    labelBgStyle: { fill: tokens.colors.neutral[0], fillOpacity: 0.8 },
    labelBgPadding: [4, 4] as [number, number],
    labelBgBorderRadius: 4,
    style: {
      stroke: tokens.colors.neutral[400],
      strokeWidth: Math.max(1, Math.min(4, Math.log10(e.frequency + 1))),
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: tokens.colors.neutral[400],
    },
    animated: false,
  }));
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export interface ProcessCanvasProps {
  dfgNodes: DFGNode[];
  dfgEdges: DFGEdge[];
  selectedNodeId?: string | null;
  highlightedPath?: string[];
  onNodeClick?: (nodeId: string) => void;
}

export function ProcessCanvas({
  dfgNodes,
  dfgEdges,
  selectedNodeId,
  highlightedPath = [],
  onNodeClick,
}: ProcessCanvasProps) {
  log.debug('Rendering ProcessCanvas', { nodeCount: dfgNodes.length, edgeCount: dfgEdges.length });

  const initialNodes = useMemo(() => {
    const nodes = layoutNodes(dfgNodes, dfgEdges);
    // Apply selection and highlight states
    return nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        isSelected: node.id === selectedNodeId,
        isHighlighted: highlightedPath.includes(node.id),
      },
    }));
  }, [dfgNodes, dfgEdges, selectedNodeId, highlightedPath]);

  const initialEdges = useMemo(() => createEdges(dfgEdges), [dfgEdges]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when selection/highlight changes
  React.useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          isSelected: node.id === selectedNodeId,
          isHighlighted: highlightedPath.includes(node.id),
        },
      }))
    );
  }, [selectedNodeId, highlightedPath, setNodes]);

  const handleNodeClick = useCallback(
    (event: React.MouseEvent, node: Node) => {
      log.debug('Node clicked', { nodeId: node.id });
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  return (
    <div style={{ width: '100%', height: '100%', backgroundColor: tokens.colors.neutral[50] }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        attributionPosition="bottom-left"
      >
        <Controls position="top-left" />
        <MiniMap
          position="bottom-right"
          nodeColor={(node) => {
            if (node.data?.isStart) return tokens.colors.success[500];
            if (node.data?.isEnd) return tokens.colors.error[500];
            if (node.data?.isHighlighted) return tokens.colors.primary[500];
            return tokens.colors.neutral[400];
          }}
          maskColor="rgba(255, 255, 255, 0.8)"
        />
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
      </ReactFlow>
    </div>
  );
}

export default ProcessCanvas;
