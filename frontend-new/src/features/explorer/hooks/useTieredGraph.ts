/**
 * useTieredGraph Hook
 *
 * Implements progressive loading for process graphs with three tiers:
 * - Overview: Aggregated view with max 50 nodes for instant loading
 * - Standard: Up to 500 nodes with moderate detail
 * - Detailed: Full graph with all nodes and edges
 *
 * This approach ensures fast initial render while allowing drill-down
 * into full detail on demand.
 */

import { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { ProcessGraphData, ProcessNode, ProcessEdge } from '../components/CytoscapeCanvas';

export type GraphTier = 'overview' | 'standard' | 'detailed';

export interface TieredGraphOptions {
  datasetId: string;
  filters?: Record<string, unknown>;
  initialTier?: GraphTier;
  enabled?: boolean;
}

export interface GraphTierConfig {
  maxNodes: number | null;
  minEdgeFrequency: number;
  aggregateSmallClusters: boolean;
}

export interface TieredGraphData {
  nodes: ProcessNode[];
  edges: ProcessEdge[];
  tier: GraphTier;
  totalNodes: number;
  totalEdges: number;
  isAggregated: boolean;
  aggregationInfo?: {
    clusteredNodes: number;
    originalNodes: number;
  };
}

export interface UseTieredGraphReturn {
  graph: TieredGraphData | null;
  currentTier: GraphTier;
  isLoading: boolean;
  isLoadingTier: GraphTier | null;
  error: Error | null;
  upgradeDetail: () => void;
  downgradeDetail: () => void;
  setTier: (tier: GraphTier) => void;
  isFullDetail: boolean;
  canUpgrade: boolean;
  canDowngrade: boolean;
  tierStats: {
    overview: { nodes: number; edges: number } | null;
    standard: { nodes: number; edges: number } | null;
    detailed: { nodes: number; edges: number } | null;
  };
}

// Tier configurations
const TIER_CONFIGS: Record<GraphTier, GraphTierConfig> = {
  overview: {
    maxNodes: 50,
    minEdgeFrequency: 100,
    aggregateSmallClusters: true,
  },
  standard: {
    maxNodes: 500,
    minEdgeFrequency: 10,
    aggregateSmallClusters: false,
  },
  detailed: {
    maxNodes: null,
    minEdgeFrequency: 1,
    aggregateSmallClusters: false,
  },
};

/**
 * Client-side graph reduction for when backend doesn't support tiered loading.
 * Reduces the graph to fit within the tier's constraints.
 */
function reduceGraphToTier(
  fullGraph: ProcessGraphData,
  tier: GraphTier
): TieredGraphData {
  const config = TIER_CONFIGS[tier];
  const { maxNodes, minEdgeFrequency, aggregateSmallClusters } = config;

  let nodes = [...fullGraph.nodes];
  let edges = [...fullGraph.edges];
  let isAggregated = false;
  let aggregationInfo: TieredGraphData['aggregationInfo'];

  // Filter edges by frequency threshold
  if (minEdgeFrequency > 1) {
    edges = edges.filter((e) => (e.frequency ?? 0) >= minEdgeFrequency);
  }

  // Get nodes that are connected by remaining edges
  const connectedNodeIds = new Set<string>();
  edges.forEach((e) => {
    connectedNodeIds.add(e.source);
    connectedNodeIds.add(e.target);
  });

  // Keep start/end nodes even if not connected by high-frequency edges
  nodes.forEach((n) => {
    if (n.isStart || n.isEnd) {
      connectedNodeIds.add(n.id);
    }
  });

  // Filter nodes to only connected ones
  nodes = nodes.filter((n) => connectedNodeIds.has(n.id));

  // If still too many nodes, aggregate low-frequency nodes
  if (maxNodes !== null && nodes.length > maxNodes) {
    isAggregated = true;
    const originalNodeCount = nodes.length;

    // Sort by frequency and keep top N
    nodes.sort((a, b) => (b.frequency ?? 0) - (a.frequency ?? 0));

    // Always keep start/end nodes
    const startEndNodes = nodes.filter((n) => n.isStart || n.isEnd);
    const otherNodes = nodes.filter((n) => !n.isStart && !n.isEnd);

    // Calculate how many regular nodes we can keep
    const regularNodeSlots = maxNodes - startEndNodes.length;
    const topNodes = otherNodes.slice(0, regularNodeSlots);

    // Create "Other" aggregation node if we're aggregating
    if (aggregateSmallClusters && otherNodes.length > regularNodeSlots) {
      const aggregatedNodes = otherNodes.slice(regularNodeSlots);
      const aggregatedFrequency = aggregatedNodes.reduce(
        (sum, n) => sum + (n.frequency ?? 0),
        0
      );

      const otherNode: ProcessNode = {
        id: '__aggregated__',
        label: `Other (${aggregatedNodes.length} activities)`,
        frequency: aggregatedFrequency,
        isStart: false,
        isEnd: false,
      };

      nodes = [...startEndNodes, ...topNodes, otherNode];

      // Update edges to point to aggregated node
      const aggregatedIds = new Set(aggregatedNodes.map((n) => n.id));
      edges = edges.map((e) => ({
        ...e,
        source: aggregatedIds.has(e.source) ? '__aggregated__' : e.source,
        target: aggregatedIds.has(e.target) ? '__aggregated__' : e.target,
      }));

      // Deduplicate edges to/from aggregated node
      const edgeMap = new Map<string, ProcessEdge>();
      edges.forEach((e) => {
        const key = `${e.source}-${e.target}`;
        const existing = edgeMap.get(key);
        if (existing) {
          existing.frequency = (existing.frequency ?? 0) + (e.frequency ?? 0);
        } else {
          edgeMap.set(key, { ...e });
        }
      });
      edges = Array.from(edgeMap.values());

      aggregationInfo = {
        clusteredNodes: aggregatedNodes.length,
        originalNodes: originalNodeCount,
      };
    } else {
      nodes = [...startEndNodes, ...topNodes];
    }

    // Remove edges that reference nodes we removed
    const nodeIds = new Set(nodes.map((n) => n.id));
    edges = edges.filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target));
  }

  return {
    nodes,
    edges,
    tier,
    totalNodes: fullGraph.nodes.length,
    totalEdges: fullGraph.edges.length,
    isAggregated,
    aggregationInfo,
  };
}

/**
 * Fetch graph data from backend with tier-specific parameters
 */
async function fetchTieredGraph(
  datasetId: string,
  tier: GraphTier,
  filters?: Record<string, unknown>
): Promise<TieredGraphData> {
  const config = TIER_CONFIGS[tier];

  // Build query params for tier
  const params = new URLSearchParams({
    ...(config.maxNodes !== null && { max_nodes: String(config.maxNodes) }),
    min_edge_frequency: String(config.minEdgeFrequency),
    aggregate: String(config.aggregateSmallClusters),
    ...(filters && Object.keys(filters).length > 0 && { filters: JSON.stringify(filters) }),
  });

  const response = await fetch(
    `/api/v1/visualization/dfg/${datasetId}/tiered?${params}`
  );

  if (!response.ok) {
    // If tiered endpoint doesn't exist, fall back to regular endpoint
    if (response.status === 404) {
      const regularResponse = await fetch(
        `/api/v1/visualization/dfg/${datasetId}`
      );
      if (!regularResponse.ok) {
        throw new Error(`Failed to fetch graph: ${regularResponse.statusText}`);
      }
      const fullGraph = await regularResponse.json();
      // Client-side reduction
      return reduceGraphToTier(fullGraph, tier);
    }
    throw new Error(`Failed to fetch tiered graph: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Hook for tiered graph loading with progressive detail enhancement
 */
export function useTieredGraph(options: TieredGraphOptions): UseTieredGraphReturn {
  const {
    datasetId,
    filters,
    initialTier = 'overview',
    enabled = true,
  } = options;

  const [currentTier, setCurrentTier] = useState<GraphTier>(initialTier);
  const [loadingTier, setLoadingTier] = useState<GraphTier | null>(null);

  // Query for overview tier (always loaded first)
  const overviewQuery = useQuery({
    queryKey: ['graph', datasetId, 'overview', filters],
    queryFn: () => fetchTieredGraph(datasetId, 'overview', filters),
    enabled: enabled && !!datasetId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Query for standard tier (loaded on demand)
  const standardQuery = useQuery({
    queryKey: ['graph', datasetId, 'standard', filters],
    queryFn: () => fetchTieredGraph(datasetId, 'standard', filters),
    enabled: enabled && !!datasetId && currentTier !== 'overview',
    staleTime: 5 * 60 * 1000,
  });

  // Query for detailed tier (loaded on demand)
  const detailedQuery = useQuery({
    queryKey: ['graph', datasetId, 'detailed', filters],
    queryFn: () => fetchTieredGraph(datasetId, 'detailed', filters),
    enabled: enabled && !!datasetId && currentTier === 'detailed',
    staleTime: 5 * 60 * 1000,
  });

  // Determine which graph to display based on current tier and available data
  const graph = useMemo((): TieredGraphData | null => {
    if (currentTier === 'detailed' && detailedQuery.data) {
      return detailedQuery.data;
    }
    if (currentTier !== 'overview' && standardQuery.data) {
      return standardQuery.data;
    }
    if (overviewQuery.data) {
      return overviewQuery.data;
    }
    return null;
  }, [currentTier, overviewQuery.data, standardQuery.data, detailedQuery.data]);

  // Loading state
  const isLoading =
    (currentTier === 'overview' && overviewQuery.isLoading) ||
    (currentTier === 'standard' && (overviewQuery.isLoading || standardQuery.isLoading)) ||
    (currentTier === 'detailed' && (overviewQuery.isLoading || detailedQuery.isLoading));

  // Error state
  const error = overviewQuery.error || standardQuery.error || detailedQuery.error;

  // Upgrade to next detail level
  const upgradeDetail = useCallback(() => {
    if (currentTier === 'overview') {
      setLoadingTier('standard');
      setCurrentTier('standard');
    } else if (currentTier === 'standard') {
      setLoadingTier('detailed');
      setCurrentTier('detailed');
    }
  }, [currentTier]);

  // Downgrade to previous detail level
  const downgradeDetail = useCallback(() => {
    if (currentTier === 'detailed') {
      setCurrentTier('standard');
    } else if (currentTier === 'standard') {
      setCurrentTier('overview');
    }
    setLoadingTier(null);
  }, [currentTier]);

  // Set specific tier
  const setTier = useCallback((tier: GraphTier) => {
    if (tier !== currentTier) {
      setLoadingTier(tier);
      setCurrentTier(tier);
    }
  }, [currentTier]);

  // Clear loading tier when query completes
  useMemo(() => {
    if (loadingTier === 'standard' && standardQuery.data) {
      setLoadingTier(null);
    }
    if (loadingTier === 'detailed' && detailedQuery.data) {
      setLoadingTier(null);
    }
  }, [loadingTier, standardQuery.data, detailedQuery.data]);

  const tierStats = useMemo(() => ({
    overview: overviewQuery.data
      ? { nodes: overviewQuery.data.nodes.length, edges: overviewQuery.data.edges.length }
      : null,
    standard: standardQuery.data
      ? { nodes: standardQuery.data.nodes.length, edges: standardQuery.data.edges.length }
      : null,
    detailed: detailedQuery.data
      ? { nodes: detailedQuery.data.nodes.length, edges: detailedQuery.data.edges.length }
      : null,
  }), [overviewQuery.data, standardQuery.data, detailedQuery.data]);

  return {
    graph,
    currentTier,
    isLoading,
    isLoadingTier: loadingTier,
    error: error as Error | null,
    upgradeDetail,
    downgradeDetail,
    setTier,
    isFullDetail: currentTier === 'detailed' && !!detailedQuery.data,
    canUpgrade: currentTier !== 'detailed',
    canDowngrade: currentTier !== 'overview',
    tierStats,
  };
}

export default useTieredGraph;
