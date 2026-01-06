/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DiscoverRequest } from '../models/DiscoverRequest';
import type { MinerInfo } from '../models/MinerInfo';
import type { ModelListResponse } from '../models/ModelListResponse';
import type { ModelResponse } from '../models/ModelResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DiscoveryService {
    /**
     * List Miners
     * List available mining algorithms.
     * @returns MinerInfo Successful Response
     * @throws ApiError
     */
    public static listMinersApiV1DiscoveryMinersGet(): CancelablePromise<Array<MinerInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/discovery/miners',
        });
    }
    /**
     * Discover Model
     * Discover a process model from an event log.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static discoverModelApiV1DiscoveryDiscoverPost({
        requestBody,
        asyncMode = true,
        xOrgId,
    }: {
        requestBody: DiscoverRequest,
        asyncMode?: boolean,
        xOrgId?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns ModelListResponse Successful Response
     * @throws ApiError
     */
    public static listModelsApiV1DiscoveryModelsGet({
        page = 1,
        pageSize = 20,
        datasetId,
    }: {
        page?: number,
        pageSize?: number,
        datasetId?: (string | null),
    }): CancelablePromise<ModelListResponse> {
        return __request(OpenAPI, {
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
     * @returns ModelResponse Successful Response
     * @throws ApiError
     */
    public static getModelApiV1DiscoveryModelsModelIdGet({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<ModelResponse> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteModelApiV1DiscoveryModelsModelIdDelete({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
