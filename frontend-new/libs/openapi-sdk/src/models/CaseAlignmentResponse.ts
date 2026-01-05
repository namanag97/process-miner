/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AlignmentMove } from './AlignmentMove';
/**
 * Alignment result for a single case.
 */
export type CaseAlignmentResponse = {
    case_id: string;
    fitness: number;
    cost?: number;
    alignment: Array<AlignmentMove>;
    is_fit?: boolean;
};

