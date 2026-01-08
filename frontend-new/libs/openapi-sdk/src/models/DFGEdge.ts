/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * DFG edge for visualization.
 */
export type DFGEdge = {
    source: string;
    target: string;
    value: number;
    probability: number;
    avg_duration_seconds?: (number | null);
    min_duration_seconds?: (number | null);
    max_duration_seconds?: (number | null);
};

