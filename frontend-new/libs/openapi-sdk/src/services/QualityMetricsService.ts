/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class QualityMetricsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Evaluate Model
     * Trigger quality evaluation for a process model.
     *
     * Computes quality metrics:
     * - **Fitness**: How well the model can replay the log (token-based replay)
     * - **Precision**: How much behavior in the model is in the log (ETC precision)
     * - **Generalization**: How well the model generalizes beyond the log
     * - **Simplicity**: Structural simplicity (arc-to-node ratio)
     *
     * Results are stored in the database and cached for future retrieval.
     * @param modelId
     * @param datasetId Dataset to evaluate against
     * @param metrics Comma-separated metrics: fitness,precision,generalization,simplicity
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public evaluateModelApiV1ModelsModelIdEvaluatePost(
        modelId: string,
        datasetId: string,
        metrics?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/models/{model_id}/evaluate',
            path: {
                'model_id': modelId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'dataset_id': datasetId,
                'metrics': metrics,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Model Metrics
     * Get stored quality metrics for a process model.
     *
     * Returns previously computed metrics without recomputation.
     * If no metrics have been computed, returns 404.
     *
     * To trigger computation, use POST /models/{id}/evaluate.
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getModelMetricsApiV1ModelsModelIdMetricsGet(
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/models/{model_id}/metrics',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
