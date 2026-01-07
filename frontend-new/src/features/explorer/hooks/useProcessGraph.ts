/**
 * useProcessGraph Hook
 * 
 * Converts backend graph_structure_json to CytoscapeCanvas props format.
 * Handles both new standardized format and legacy DFG format.
 */

import { useMemo } from 'react';
import type { ProcessGraphData, ProcessNode, ProcessEdge } from '../components/CytoscapeCanvas';

export interface GraphStructureJSON {
    nodes: Array<{
        id: string;
        label: string;
        type: 'activity' | 'place' | 'transition';
        frequency?: number;
        is_start?: boolean;
        is_end?: boolean;
        attributes?: Record<string, unknown>;
    }>;
    edges: Array<{
        id: string;
        source: string;
        target: string;
        frequency?: number;
        probability?: number;
        attributes?: Record<string, unknown>;
    }>;
    metadata?: {
        node_count: number;
        edge_count: number;
        type: string;
        source_format?: string;
    };
    start_activities?: Record<string, number>;
    end_activities?: Record<string, number>;
    total_frequency?: number;
}

export interface LegacyDFGData {
    nodes: Array<{
        id: string;
        label: string;
        frequency?: number;
        isStart?: boolean;
        isEnd?: boolean;
    }>;
    edges: Array<{
        source: string;
        target: string;
        frequency?: number;
        avgDuration?: number;
    }>;
    startActivities?: Record<string, number>;
    endActivities?: Record<string, number>;
    totalFrequency?: number;
}

/**
 * Convert new graph_structure_json format to CytoscapeCanvas props
 */
function convertNewFormat(data: GraphStructureJSON): ProcessGraphData {
    const nodes: ProcessNode[] = data.nodes.map((node: any) => ({
        id: node.id,
        label: node.label,
        frequency: node.frequency,
        isStart: node.is_start,
        isEnd: node.is_end,
    }));

    const edges: ProcessEdge[] = data.edges.map((edge: any) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        frequency: edge.frequency,
        probability: edge.probability,
    }));

    return {
        nodes,
        edges,
        startActivities: data.start_activities,
        endActivities: data.end_activities,
        totalFrequency: data.total_frequency,
        metadata: data.metadata ? {
            nodeCount: data.metadata.node_count,
            edgeCount: data.metadata.edge_count,
            type: data.metadata.type,
        } : undefined,
    };
}

/**
 * Convert legacy DFG format to CytoscapeCanvas props
 */
function convertLegacyFormat(data: LegacyDFGData): ProcessGraphData {
    const nodes: ProcessNode[] = data.nodes.map((node: any) => ({
        id: node.id,
        label: node.label,
        frequency: node.frequency,
        isStart: node.isStart,
        isEnd: node.isEnd,
    }));

    const edges: ProcessEdge[] = data.edges.map((edge, index) => ({
        id: `edge-${edge.source}-${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        frequency: edge.frequency,
    }));

    return {
        nodes,
        edges,
        startActivities: data.startActivities,
        endActivities: data.endActivities,
        totalFrequency: data.totalFrequency,
    };
}

/**
 * Detect if data is in new graph_structure_json format
 */
function isNewFormat(data: unknown): data is GraphStructureJSON {
    if (!data || typeof data !== 'object') return false;
    const obj = data as Record<string, unknown>;

    // New format has snake_case keys and type field on nodes
    if (Array.isArray(obj.nodes) && obj.nodes.length > 0) {
        const firstNode = obj.nodes[0] as Record<string, unknown>;
        return 'type' in firstNode || 'is_start' in firstNode;
    }
    return false;
}

/**
 * Hook to convert backend graph data to CytoscapeCanvas format
 */
export function useProcessGraph(
    data: GraphStructureJSON | LegacyDFGData | null | undefined
): ProcessGraphData | null {
    return useMemo(() => {
        if (!data) return null;

        if (isNewFormat(data)) {
            return convertNewFormat(data);
        }

        return convertLegacyFormat(data as LegacyDFGData);
    }, [data]);
}

export default useProcessGraph;
