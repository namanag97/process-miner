/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OCDFGTypeGraph } from './OCDFGTypeGraph';
/**
 * Object-Centric DFG response.
 */
export type OCDFGResponse = {
    log_id: string;
    object_types: Array<string>;
    activities: Array<string>;
    graphs_by_type: Record<string, OCDFGTypeGraph>;
    total_events?: number;
    total_objects?: number;
};

