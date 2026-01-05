/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PredictionResponse } from './PredictionResponse';
/**
 * Batch prediction results.
 */
export type BatchPredictionResponse = {
    predictor_id: string;
    predictions: Array<PredictionResponse>;
};

