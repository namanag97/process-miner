/**
 * ProcessCanvas - Advanced Process Graph Visualization
 *
 * Features:
 * - Dagre hierarchical layout
 * - Enhanced activity nodes with rich visuals
 * - Performance-based coloring
 * - Dynamic edge thickness based on frequency
 * - Interactive controls (layout, metrics, animation)
 * - MiniMap and zoom controls
 */

import React, { useCallback, useMemo, useEffect, useState } from 'react';
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
  Panel,
  useReactFlow,
  ReactFlowProvider,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Button, Segmented, Tooltip, Space, Switch, Slider } from 'antd';
import {
  AimOutlined,
  ColumnHeightOutlined,
  ColumnWidthOutlined,
  ThunderboltOutlined,
  ClockCircleOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  FullscreenOutlined,
} from '@ant-design/icons';
import { tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

// Import utilities and custom nodes
import { EnhancedActivityNode, EnhancedActivityNodeData } from './EnhancedActivityNode';
import {
  applyDagreLayout,
  LayoutDirection,
  calculateNodeScale,
} from '../utils/layoutAlgorithms';
import {
  getPerformanceColor,
  getEdgeStyle,
  calculateStats,
  formatDuration,
  formatNumber,
  COLORS,
} from '../utils/colorScales';

const log = createLogger('ProcessCanvas');

// =============================================================================
// TYPES
// =============================================================================

export interface DFGNodeData {
  id: string;
  label: string;
  frequency: number;
  isStart?: boolean;
  isEnd?: boolean;
  avgDuration?: number;
  minDuration?: number;
  maxDuration?: number;
}

export interface DFGEdgeData {
  source: string;
  target: string;
  frequency: number;
  performance?: number;  // avg duration in seconds
}

export type MetricMode = 'frequency' | 'performance';

export interface ProcessCanvasProps {
  dfgNodes: DFGNodeData[];
  dfgEdges: DFGEdgeData[];
  selectedNodeId?: string | null;
  selectedEdgeId?: string | null;
  highlightedPath?: string[];
  onNodeClick?: (nodeId: string) => void;
  onEdgeClick?: (edgeId: string, source: string, target: string) => void;
  onLayoutChange?: (direction: LayoutDirection) => void;
}

// =============================================================================
// NODE TYPES REGISTRATION
// =============================================================================

const nodeTypes = {
  enhanced: EnhancedActivityNode,
};

// =============================================================================
// INNER CANVAS (with ReactFlow hooks)
// =============================================================================

interface InnerCanvasProps extends ProcessCanvasProps {
  layoutDirection: LayoutDirection;
  metricMode: MetricMode;
  showAnimation: boolean;
  complexityThreshold: number;
}

function InnerCanvas({
  dfgNodes,
  dfgEdges,
  selectedNodeId,
  selectedEdgeId,
  highlightedPath = [],
  onNodeClick,
  onEdgeClick,
  layoutDirection,
  metricMode,
  showAnimation,
  complexityThreshold,
}: InnerCanvasProps) {
  const { fitView } = useReactFlow();

  // Calculate frequency/duration statistics
  const stats = useMemo(() => {
    const frequencies = dfgNodes.map((n) => n.frequency);
    const durations = dfgEdges
      .map((e) => e.performance)
      .filter((d): d is number => d !== undefined && d > 0);

    return {
      frequency: calculateStats(frequencies),
      duration: calculateStats(durations),
    };
  }, [dfgNodes, dfgEdges]);

  // Filter edges by complexity threshold
  const filteredEdges = useMemo(() => {
    if (complexityThreshold >= 100) return dfgEdges;

    const sortedByFreq = [...dfgEdges].sort((a, b) => b.frequency - a.frequency);
    const totalFreq = sortedByFreq.reduce((sum, e) => sum + e.frequency, 0);
    const threshold = totalFreq * (complexityThreshold / 100);

    let cumulative = 0;
    return sortedByFreq.filter((edge) => {
      cumulative += edge.frequency;
      return cumulative <= threshold || edge.frequency === sortedByFreq[0].frequency;
    });
  }, [dfgEdges, complexityThreshold]);

  // Build ReactFlow nodes with enhanced data
  const processedNodes = useMemo(() => {
    const showPerformance = metricMode === 'performance';

    return dfgNodes.map((node): Node<EnhancedActivityNodeData> => {
      const scale = calculateNodeScale(
        node.frequency,
        stats.frequency.max,
        stats.frequency.min
      );

      // Calculate performance color if in performance mode
      let performanceColor: string | undefined;
      if (showPerformance && node.avgDuration !== undefined) {
        performanceColor = getPerformanceColor(
          node.avgDuration,
          stats.duration.min,
          stats.duration.max
        );
      }

      return {
        id: node.id,
        type: 'enhanced',
        position: { x: 0, y: 0 }, // Will be set by layout
        data: {
          label: node.label,
          frequency: node.frequency,
          frequencyPercent: (node.frequency / stats.frequency.max) * 100,
          avgDuration: node.avgDuration,
          minDuration: node.minDuration,
          maxDuration: node.maxDuration,
          isStart: node.isStart,
          isEnd: node.isEnd,
          isSelected: node.id === selectedNodeId,
          isHighlighted: highlightedPath.includes(node.id),
          showPerformance,
          performanceColor,
          scale,
        },
      };
    });
  }, [dfgNodes, selectedNodeId, highlightedPath, metricMode, stats]);

  // Build ReactFlow edges with styling
  const processedEdges = useMemo(() => {
    const showPerformance = metricMode === 'performance';

    return filteredEdges.map((edge, index): Edge => {
      const edgeId = `e-${edge.source}-${edge.target}`;
      const isSelected = edgeId === selectedEdgeId;
      const isHighlighted =
        highlightedPath.includes(edge.source) &&
        highlightedPath.includes(edge.target) &&
        highlightedPath.indexOf(edge.target) === highlightedPath.indexOf(edge.source) + 1;

      // Calculate edge style
      const edgeStyle = getEdgeStyle(
        edge.frequency,
        stats.frequency.min,
        stats.frequency.max,
        edge.performance,
        stats.duration.min,
        stats.duration.max,
        showPerformance
      );

      // Determine stroke color
      let strokeColor = edgeStyle.stroke;
      if (isSelected) {
        strokeColor = COLORS.edge.selected;
      } else if (isHighlighted) {
        strokeColor = COLORS.edge.highlighted;
      }

      // Edge label
      const label = showPerformance && edge.performance
        ? formatDuration(edge.performance)
        : formatNumber(edge.frequency);

      return {
        id: edgeId,
        source: edge.source,
        target: edge.target,
        type: 'smoothstep',
        label,
        labelStyle: {
          fontSize: 10,
          fontWeight: isHighlighted ? 600 : 400,
          fill: isHighlighted ? COLORS.edge.highlighted : tokens.colors.neutral[600],
        },
        labelBgStyle: {
          fill: tokens.colors.neutral[0],
          fillOpacity: 0.85,
        },
        labelBgPadding: [4, 6] as [number, number],
        labelBgBorderRadius: 4,
        style: {
          stroke: strokeColor,
          strokeWidth: isSelected || isHighlighted ? edgeStyle.strokeWidth + 1 : edgeStyle.strokeWidth,
          opacity: isHighlighted ? 1 : edgeStyle.opacity,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: strokeColor,
          width: 16,
          height: 16,
        },
        animated: showAnimation && (isHighlighted || edgeStyle.animated),
        data: { frequency: edge.frequency, performance: edge.performance },
      };
    });
  }, [filteredEdges, selectedEdgeId, highlightedPath, metricMode, showAnimation, stats]);

  // Apply dagre layout
  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(() => {
    return applyDagreLayout(processedNodes, processedEdges, {
      direction: layoutDirection,
      nodeWidth: 180,
      nodeHeight: 80,
      rankSep: 100,
      nodeSep: 50,
    });
  }, [processedNodes, processedEdges, layoutDirection]);

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  // Update when layout changes
  useEffect(() => {
    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
    setTimeout(() => fitView({ padding: 0.15, duration: 300 }), 50);
  }, [layoutedNodes, layoutedEdges, setNodes, setEdges, fitView]);

  // Handlers
  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      log.debug('Node clicked', { nodeId: node.id });
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  const handleEdgeClick = useCallback(
    (_event: React.MouseEvent, edge: Edge) => {
      log.debug('Edge clicked', { edgeId: edge.id });
      onEdgeClick?.(edge.id, edge.source, edge.target);
    },
    [onEdgeClick]
  );

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={handleNodeClick}
      onEdgeClick={handleEdgeClick}
      nodeTypes={nodeTypes}
      fitView
      fitViewOptions={{ padding: 0.15 }}
      minZoom={0.1}
      maxZoom={2}
      attributionPosition="bottom-left"
      proOptions={{ hideAttribution: true }}
      defaultEdgeOptions={{
        type: 'smoothstep',
      }}
    >
      <Controls
        position="bottom-left"
        showInteractive={false}
        style={{
          display: 'flex',
          flexDirection: 'row',
          gap: 4,
          background: 'white',
          borderRadius: 8,
          padding: 4,
          boxShadow: tokens.shadow.md,
        }}
      />
      <MiniMap
        position="bottom-right"
        nodeColor={(node) => {
          const data = node.data as EnhancedActivityNodeData;
          if (data?.isStart) return COLORS.border.start;
          if (data?.isEnd) return COLORS.border.end;
          if (data?.isHighlighted) return COLORS.edge.highlighted;
          if (data?.showPerformance && data?.performanceColor) return data.performanceColor;
          return tokens.colors.neutral[400];
        }}
        maskColor="rgba(255, 255, 255, 0.85)"
        style={{
          borderRadius: 8,
          overflow: 'hidden',
          boxShadow: tokens.shadow.md,
        }}
        pannable
        zoomable
      />
      <Background
        variant={BackgroundVariant.Dots}
        gap={20}
        size={1}
        color={tokens.colors.neutral[300]}
      />
    </ReactFlow>
  );
}

// =============================================================================
// MAIN COMPONENT WITH CONTROLS
// =============================================================================

export function ProcessCanvas(props: ProcessCanvasProps) {
  const { dfgNodes, dfgEdges, onLayoutChange } = props;

  // Control state
  const [layoutDirection, setLayoutDirection] = useState<LayoutDirection>('LR');
  const [metricMode, setMetricMode] = useState<MetricMode>('frequency');
  const [showAnimation, setShowAnimation] = useState(false);
  const [complexityThreshold, setComplexityThreshold] = useState(100);

  // Handle layout change
  const handleLayoutChange = useCallback(
    (direction: LayoutDirection) => {
      setLayoutDirection(direction);
      onLayoutChange?.(direction);
    },
    [onLayoutChange]
  );

  log.debug('Rendering ProcessCanvas', {
    nodeCount: dfgNodes.length,
    edgeCount: dfgEdges.length,
    layout: layoutDirection,
    metric: metricMode,
  });

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }}>
      {/* Graph Controls Toolbar */}
      <div
        style={{
          position: 'absolute',
          top: 12,
          left: 12,
          right: 12,
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: 8,
        }}
      >
        {/* Left Controls: Layout */}
        <Space
          style={{
            background: 'white',
            borderRadius: 8,
            padding: '6px 12px',
            boxShadow: tokens.shadow.md,
          }}
        >
          <Tooltip title="Layout Direction">
            <Segmented
              size="small"
              value={layoutDirection}
              onChange={(value) => handleLayoutChange(value as LayoutDirection)}
              options={[
                {
                  value: 'LR',
                  icon: <ColumnWidthOutlined />,
                  label: '',
                },
                {
                  value: 'TB',
                  icon: <ColumnHeightOutlined />,
                  label: '',
                },
              ]}
            />
          </Tooltip>
        </Space>

        {/* Center Controls: Metrics & Animation */}
        <Space
          style={{
            background: 'white',
            borderRadius: 8,
            padding: '6px 12px',
            boxShadow: tokens.shadow.md,
          }}
        >
          <Tooltip title="Display Metric">
            <Segmented
              size="small"
              value={metricMode}
              onChange={(value) => setMetricMode(value as MetricMode)}
              options={[
                {
                  value: 'frequency',
                  icon: <ThunderboltOutlined />,
                  label: 'Frequency',
                },
                {
                  value: 'performance',
                  icon: <ClockCircleOutlined />,
                  label: 'Duration',
                },
              ]}
            />
          </Tooltip>

          <div
            style={{
              width: 1,
              height: 20,
              backgroundColor: tokens.colors.neutral[200],
            }}
          />

          <Tooltip title="Animate Flow">
            <Switch
              size="small"
              checked={showAnimation}
              onChange={setShowAnimation}
              checkedChildren={<PlayCircleOutlined />}
              unCheckedChildren={<PauseCircleOutlined />}
            />
          </Tooltip>
        </Space>

        {/* Right Controls: Complexity Slider */}
        <Space
          style={{
            background: 'white',
            borderRadius: 8,
            padding: '6px 16px',
            boxShadow: tokens.shadow.md,
            minWidth: 180,
          }}
        >
          <Tooltip title="Show top X% of paths by frequency">
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontSize: 11, color: tokens.colors.neutral[500], whiteSpace: 'nowrap' }}>
                Paths:
              </span>
              <Slider
                min={20}
                max={100}
                step={10}
                value={complexityThreshold}
                onChange={setComplexityThreshold}
                tooltip={{ formatter: (v) => `Top ${v}%` }}
                style={{ width: 100, margin: 0 }}
              />
              <span style={{ fontSize: 11, fontWeight: 500, minWidth: 32 }}>
                {complexityThreshold}%
              </span>
            </div>
          </Tooltip>
        </Space>
      </div>

      {/* ReactFlow Canvas */}
      <div style={{ width: '100%', height: '100%', backgroundColor: tokens.colors.neutral[50] }}>
        <ReactFlowProvider>
          <InnerCanvas
            {...props}
            layoutDirection={layoutDirection}
            metricMode={metricMode}
            showAnimation={showAnimation}
            complexityThreshold={complexityThreshold}
          />
        </ReactFlowProvider>
      </div>
    </div>
  );
}

export default ProcessCanvas;
