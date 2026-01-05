/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NetworkEdge } from './NetworkEdge';
import type { NetworkNode } from './NetworkNode';
/**
 * Social network response.
 */
export type SocialNetworkResponse = {
    dataset_id: string;
    network_type: string;
    nodes: Array<NetworkNode>;
    edges: Array<NetworkEdge>;
    metrics: Record<string, any>;
};

