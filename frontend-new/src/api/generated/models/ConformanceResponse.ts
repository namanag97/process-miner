/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Conformance check result.
 */
export type ConformanceResponse = {
    id: string;
    dataset_id: string;
    model_id: string;
    fitness: number;
    precision: (number | null);
    generalization?: (number | null);
    simplicity?: (number | null);
    method: string;
    algorithm_used: string;
    fallback_reason?: (string | null);
    is_conformant: boolean;
    fitting_traces: number;
    total_traces: number;
    created_at: string;
};

