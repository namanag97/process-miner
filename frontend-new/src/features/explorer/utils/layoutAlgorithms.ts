/**
 * Graph Layout Algorithms for Process Explorer
 * Uses dagre for hierarchical directed graph layout
 */

import dagre from 'dagre';
import { Node, Edge, Position } from 'reactflow';

export type LayoutDirection = 'TB' | 'LR' | 'BT' | 'RL';

export interface LayoutOptions {
  direction: LayoutDirection;
  nodeWidth: number;
  nodeHeight: number;
  rankSep: number;  // Separation between ranks (layers)
  nodeSep: number;  // Separation between nodes in same rank
  edgeSep: number;  // Separation between edges
  marginX: number;
  marginY: number;
}

const DEFAULT_OPTIONS: LayoutOptions = {
  direction: 'LR',
  nodeWidth: 180,
  nodeHeight: 80,
  rankSep: 80,
  nodeSep: 40,
  edgeSep: 20,
  marginX: 50,
  marginY: 50,
};

/**
 * Apply dagre layout to nodes and edges
 */
export function applyDagreLayout<T>(
  nodes: Node<T>[],
  edges: Edge[],
  options: Partial<LayoutOptions> = {}
): { nodes: Node<T>[]; edges: Edge[] } {
  const opts = { ...DEFAULT_OPTIONS, ...options };

  // Create dagre graph
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  dagreGraph.setGraph({
    rankdir: opts.direction,
    ranksep: opts.rankSep,
    nodesep: opts.nodeSep,
    edgesep: opts.edgeSep,
    marginx: opts.marginX,
    marginy: opts.marginY,
  });

  // Add nodes to dagre
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, {
      width: opts.nodeWidth,
      height: opts.nodeHeight,
    });
  });

  // Add edges to dagre
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  // Run layout
  dagre.layout(dagreGraph);

  // Get source/target handle positions based on direction
  const { sourcePosition, targetPosition } = getHandlePositions(opts.direction);

  // Apply positions to nodes
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);

    return {
      ...node,
      position: {
        x: nodeWithPosition.x - opts.nodeWidth / 2,
        y: nodeWithPosition.y - opts.nodeHeight / 2,
      },
      sourcePosition,
      targetPosition,
    };
  });

  return { nodes: layoutedNodes, edges };
}

/**
 * Get handle positions based on layout direction
 */
function getHandlePositions(direction: LayoutDirection): {
  sourcePosition: Position;
  targetPosition: Position;
} {
  switch (direction) {
    case 'TB':
      return { sourcePosition: Position.Bottom, targetPosition: Position.Top };
    case 'BT':
      return { sourcePosition: Position.Top, targetPosition: Position.Bottom };
    case 'RL':
      return { sourcePosition: Position.Left, targetPosition: Position.Right };
    case 'LR':
    default:
      return { sourcePosition: Position.Right, targetPosition: Position.Left };
  }
}

/**
 * Calculate node importance based on frequency
 * Returns a scale factor for node sizing (0.7 to 1.3)
 */
export function calculateNodeScale(
  frequency: number,
  maxFrequency: number,
  minFrequency: number
): number {
  if (maxFrequency === minFrequency) return 1;
  const normalized = (frequency - minFrequency) / (maxFrequency - minFrequency);
  return 0.8 + normalized * 0.4; // Range: 0.8 to 1.2
}

/**
 * Calculate edge thickness based on frequency
 * Returns stroke width (1 to 8)
 */
export function calculateEdgeWidth(
  frequency: number,
  maxFrequency: number,
  minFrequency: number
): number {
  if (maxFrequency === minFrequency) return 2;
  const normalized = (frequency - minFrequency) / (maxFrequency - minFrequency);
  return 1 + normalized * 7; // Range: 1 to 8
}

/**
 * Auto-detect optimal layout direction based on graph shape
 */
export function detectOptimalDirection(
  nodes: Node[],
  edges: Edge[]
): LayoutDirection {
  // Calculate in-degree and out-degree for each node
  const inDegree = new Map<string, number>();
  const outDegree = new Map<string, number>();

  nodes.forEach((n) => {
    inDegree.set(n.id, 0);
    outDegree.set(n.id, 0);
  });

  edges.forEach((e) => {
    inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
    outDegree.set(e.source, (outDegree.get(e.source) || 0) + 1);
  });

  // Count nodes with no incoming edges (start nodes)

  // If there are more start/end nodes than the graph is wide, use TB
  // Otherwise use LR (typical process flow)
  const avgBranching = edges.length / Math.max(nodes.length, 1);

  if (avgBranching > 2 || nodes.length > 15) {
    return 'TB'; // Top to bottom for complex graphs
  }

  return 'LR'; // Left to right for linear processes
}

/**
 * Calculate graph statistics for display
 */
export interface GraphStats {
  nodeCount: number;
  edgeCount: number;
  maxDepth: number;
  avgBranching: number;
  startNodes: string[];
  endNodes: string[];
  hasCycles: boolean;
}

export function calculateGraphStats(
  nodes: Node[],
  edges: Edge[]
): GraphStats {
  const inDegree = new Map<string, number>();
  const outDegree = new Map<string, number>();
  const adjacency = new Map<string, string[]>();

  nodes.forEach((n) => {
    inDegree.set(n.id, 0);
    outDegree.set(n.id, 0);
    adjacency.set(n.id, []);
  });

  edges.forEach((e) => {
    inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
    outDegree.set(e.source, (outDegree.get(e.source) || 0) + 1);
    adjacency.get(e.source)?.push(e.target);
  });

  const startNodes = nodes
    .filter((n) => (inDegree.get(n.id) || 0) === 0)
    .map((n) => n.id);
  const endNodes = nodes
    .filter((n) => (outDegree.get(n.id) || 0) === 0)
    .map((n) => n.id);

  // Calculate max depth using BFS
  let maxDepth = 0;
  if (startNodes.length > 0) {
    const visited = new Set<string>();
    const queue: Array<{ id: string; depth: number }> = startNodes.map((id) => ({
      id,
      depth: 0,
    }));

    while (queue.length > 0) {
      const { id, depth } = queue.shift()!;
      if (visited.has(id)) continue;
      visited.add(id);
      maxDepth = Math.max(maxDepth, depth);

      const neighbors = adjacency.get(id) || [];
      neighbors.forEach((neighbor) => {
        if (!visited.has(neighbor)) {
          queue.push({ id: neighbor, depth: depth + 1 });
        }
      });
    }
  }

  // Simple cycle detection (if visited count < node count, there might be cycles)
  const hasCycles = edges.length >= nodes.length;

  return {
    nodeCount: nodes.length,
    edgeCount: edges.length,
    maxDepth,
    avgBranching: nodes.length > 0 ? edges.length / nodes.length : 0,
    startNodes,
    endNodes,
    hasCycles,
  };
}
