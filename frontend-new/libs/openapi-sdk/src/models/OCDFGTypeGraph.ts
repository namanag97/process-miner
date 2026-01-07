/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OCDFGEdge } from './OCDFGEdge';
import type { OCDFGNode } from './OCDFGNode';
/**
 * OC-DFG graph for a single object type.
 */
export type OCDFGTypeGraph = {
    object_type: string;
    nodes: Array<OCDFGNode>;
    edges: Array<OCDFGEdge>;
    start_activities?: Array<string>;
    end_activities?: Array<string>;
};

