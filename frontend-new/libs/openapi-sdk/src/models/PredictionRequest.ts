/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request for a single prediction.
 */
export type PredictionRequest = {
    /**
     * Activity sequence so far
     */
    case_prefix: Array<string>;
    case_attributes?: (Record<string, any> | null);
};

