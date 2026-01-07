/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Prediction result.
 */
export type PredictionResponse = {
    predictor_id: string;
    case_prefix: Array<string>;
    prediction: any;
    confidence: (number | null);
    alternatives?: null;
};

