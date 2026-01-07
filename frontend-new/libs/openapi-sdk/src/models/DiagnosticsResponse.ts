/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeviationDetail } from './DeviationDetail';
/**
 * Detailed conformance diagnostics.
 */
export type DiagnosticsResponse = {
    fitness: number;
    precision: (number | null);
    generalization?: (number | null);
    simplicity?: (number | null);
    f_score?: (number | null);
    total_traces: number;
    fitting_traces: number;
    non_fitting_traces: number;
    fitness_ratio: number;
    average_alignment_cost?: (number | null);
    deviations?: (Array<DeviationDetail> | null);
};

