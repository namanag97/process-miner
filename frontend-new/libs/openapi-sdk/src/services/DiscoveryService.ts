/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DiscoverRequest } from '../models/DiscoverRequest';
import type { MinerInfo } from '../models/MinerInfo';
import type { ModelListResponse } from '../models/ModelListResponse';
import type { ModelResponse } from '../models/ModelResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DiscoveryService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Miners
     * List available mining algorithms.
     *
     * Returns information about each algorithm including its output format.
     * @returns MinerInfo Successful Response
     * @throws ApiError
     */
    public listMinersApiV1DiscoveryMinersGet(): CancelablePromise<Array<MinerInfo>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/discovery/miners',
        });
    }
    /**
     * Discover Model
     * Discover a process model from an event log.
     *
     * BUG-019 FIX: Heavy mining is now offloaded to Celery by default.
     * Set async_mode=False for synchronous execution (not recommended for large logs).
     *
     * Args:
     * request: Discovery request with dataset_id, miner_type, model_name
     * async_mode: If True (default), runs in background and returns job_id
     *
     * Returns:
     * - If async_mode=True: {"job_id": "...", "status": "pending"}
     * - If async_mode=False: ModelResponse with discovered model
     * @param requestBody
     * @param asyncMode
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public discoverModelApiV1DiscoveryDiscoverPost(
        requestBody: DiscoverRequest,
        asyncMode: boolean = true,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/discovery/discover',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'async_mode': asyncMode,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Models
     * List discovered process models.
     *
     * Supports pagination and filtering by source dataset.
     * @param page
     * @param pageSize
     * @param datasetId
     * @returns ModelListResponse Successful Response
     * @throws ApiError
     */
    public listModelsApiV1DiscoveryModelsGet(
        page: number = 1,
        pageSize: number = 20,
        datasetId?: (string | null),
    ): CancelablePromise<ModelListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/discovery/models',
            query: {
                'page': page,
                'page_size': pageSize,
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Model
     * Get details of a discovered process model.
     * @param modelId
     * @returns ModelResponse Successful Response
     * @throws ApiError
     */
    public getModelApiV1DiscoveryModelsModelIdGet(
        modelId: string,
    ): CancelablePromise<ModelResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/discovery/models/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Model
     * Delete a discovered process model.
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteModelApiV1DiscoveryModelsModelIdDelete(
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/discovery/models/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
