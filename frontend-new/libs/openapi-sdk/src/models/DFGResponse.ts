/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DFGEdge } from './DFGEdge';
import type { DFGNode } from './DFGNode';
/**
 * DFG graph data for React visualization.
 */
export type DFGResponse = {
    nodes: Array<DFGNode>;
    edges: Array<DFGEdge>;
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
    total_frequency: number;
};

