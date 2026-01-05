/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BatchPredictionRequest } from '../models/BatchPredictionRequest';
import type { BatchPredictionResponse } from '../models/BatchPredictionResponse';
import type { PredictionRequest } from '../models/PredictionRequest';
import type { PredictionResponse } from '../models/PredictionResponse';
import type { PredictorListResponse } from '../models/PredictorListResponse';
import type { PredictorResponse } from '../models/PredictorResponse';
import type { TrainPredictorRequest } from '../models/TrainPredictorRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class PredictionsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Train Predictor
     * Train a prediction model for an event log.
     *
     * Args:
     * log_id: Event log ID
     * request: Training request with target_type and algorithm
     * async_mode: If True, train asynchronously via Celery (default)
     *
     * Returns:
     * - If async_mode=True: {"job_id": "...", "status": "pending"}
     * - If async_mode=False: PredictorResponse with trained model
     * @param logId
     * @param requestBody
     * @param asyncMode
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public trainPredictorApiV1PredictionsLogsLogIdTrainPost(
        logId: string,
        requestBody: TrainPredictorRequest,
        asyncMode: boolean = true,
        userId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/predictions/logs/{log_id}/train',
            path: {
                'log_id': logId,
            },
            query: {
                'async_mode': asyncMode,
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Status
     * Get status of an async training job.
     *
     * Args:
     * job_id: Celery task ID
     * user_id: Optional user ID for ownership validation (BUG-046)
     *
     * Returns:
     * Job status with progress information
     * @param jobId
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getJobStatusApiV1PredictionsJobsJobIdGet(
        jobId: string,
        userId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/predictions/jobs/{job_id}',
            path: {
                'job_id': jobId,
            },
            query: {
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Predictors
     * List all predictors for an event log.
     * @param logId
     * @returns PredictorListResponse Successful Response
     * @throws ApiError
     */
    public listPredictorsApiV1PredictionsLogsLogIdPredictorsGet(
        logId: string,
    ): CancelablePromise<PredictorListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/predictions/logs/{log_id}/predictors',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Predictor
     * Get predictor details.
     * @param predictorId
     * @returns PredictorResponse Successful Response
     * @throws ApiError
     */
    public getPredictorApiV1PredictionsPredictorsPredictorIdGet(
        predictorId: string,
    ): CancelablePromise<PredictorResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/predictions/predictors/{predictor_id}',
            path: {
                'predictor_id': predictorId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Predictor
     * Delete a predictor.
     * @param predictorId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deletePredictorApiV1PredictionsPredictorsPredictorIdDelete(
        predictorId: string,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/predictions/predictors/{predictor_id}',
            path: {
                'predictor_id': predictorId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Predict
     * Make a prediction for a case prefix.
     * @param predictorId
     * @param requestBody
     * @returns PredictionResponse Successful Response
     * @throws ApiError
     */
    public predictApiV1PredictionsPredictorsPredictorIdPredictPost(
        predictorId: string,
        requestBody: PredictionRequest,
    ): CancelablePromise<PredictionResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/predictions/predictors/{predictor_id}/predict',
            path: {
                'predictor_id': predictorId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Predict Batch
     * Make batch predictions.
     * @param predictorId
     * @param requestBody
     * @returns BatchPredictionResponse Successful Response
     * @throws ApiError
     */
    public predictBatchApiV1PredictionsPredictorsPredictorIdPredictBatchPost(
        predictorId: string,
        requestBody: BatchPredictionRequest,
    ): CancelablePromise<BatchPredictionResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/predictions/predictors/{predictor_id}/predict-batch',
            path: {
                'predictor_id': predictorId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
