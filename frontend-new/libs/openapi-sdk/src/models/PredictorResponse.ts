/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Prediction model response.
 */
export type PredictorResponse = {
    id: string;
    log_id?: string;
    target_type: string;
    algorithm: string;
    metrics?: Record<string, any>;
    trained_at?: (string | null);
};

