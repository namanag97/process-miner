/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CaseAlignmentResponse } from './CaseAlignmentResponse';
/**
 * Response for alignment diagnostics endpoint.
 */
export type AlignmentDiagnosticsResponse = {
    log_id: string;
    model_id: string;
    total_cases: number;
    fitting_cases: number;
    average_fitness: number;
    case_alignments: Array<CaseAlignmentResponse>;
};

