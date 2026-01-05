/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Full quality metrics for a process model.
 *
 * Contains all 4 quality dimensions from PM4py:
 * - Fitness: How well the log fits the model
 * - Precision: How much the model allows for behavior not in the log
 * - Generalization: How well the model generalizes beyond observed behavior
 * - Simplicity: How simple/understandable the model is
 */
export type QualityMetricsResponse = {
    log_id: string;
    model_id: string;
    fitness: number;
    precision?: (number | null);
    generalization?: (number | null);
    simplicity?: (number | null);
    f_score?: (number | null);
};

