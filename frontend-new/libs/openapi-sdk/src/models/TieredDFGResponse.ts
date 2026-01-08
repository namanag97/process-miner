/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DFGEdge } from './DFGEdge';
import type { DFGNode } from './DFGNode';
import type { TieredDFGAggregationInfo } from './TieredDFGAggregationInfo';
/**
 * Tiered DFG response for progressive loading.
 *
 * Supports three tiers:
 * - overview: Max 50 nodes, high-frequency edges only
 * - standard: Max 500 nodes, moderate edge filtering
 * - detailed: Full graph with all nodes and edges
 *
 * This enables fast initial rendering with progressive detail enhancement.
 */
export type TieredDFGResponse = {
    nodes: Array<DFGNode>;
    edges: Array<DFGEdge>;
    tier: string;
    total_nodes: number;
    total_edges: number;
    is_aggregated: boolean;
    aggregation_info?: (TieredDFGAggregationInfo | null);
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
};

