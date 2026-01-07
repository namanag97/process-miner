/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PredictorResponse } from './PredictorResponse';
/**
 * List of prediction models.
 */
export type PredictorListResponse = {
    dataset_id: string;
    predictors: Array<PredictorResponse>;
    total: number;
};

