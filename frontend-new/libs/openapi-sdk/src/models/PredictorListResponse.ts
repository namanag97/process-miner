/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PredictorResponse } from './PredictorResponse';
/**
 * List of prediction models.
 */
export type PredictorListResponse = {
    log_id: string;
    predictors: Array<PredictorResponse>;
    total: number;
};

