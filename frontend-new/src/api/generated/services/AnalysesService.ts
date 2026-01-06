/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalysisCreateRequest } from '../models/AnalysisCreateRequest';
import type { AnalysisDetailResponse } from '../models/AnalysisDetailResponse';
import type { AnalysisListResponse } from '../models/AnalysisListResponse';
import type { AnalysisResponse } from '../models/AnalysisResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnalysesService {
    /**
     * Get Analysis Metadata
     * Get metadata for all available analysis types.
     *
     * This endpoint enables dynamic UI generation - the frontend can discover
     * all available analysis types, their configuration schemas, and result types
     * without hardcoding them.
     *
     * Returns a registry of 70+ analysis types with their schemas.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAnalysisMetadataApiV1AnalysesMetadataGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analyses/metadata',
        });
    }
    /**
     * Create Analysis
     * Create a new analysis for an event log.
     *
     * The analysis will be queued for processing and status updated when complete.
     * @returns AnalysisResponse Successful Response
     * @throws ApiError
     */
    public static createAnalysisApiV1AnalysesPost({
        datasetId,
        requestBody,
    }: {
        datasetId: string,
        requestBody: AnalysisCreateRequest,
    }): CancelablePromise<AnalysisResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/analyses',
            query: {
                'dataset_id': datasetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Analyses
     * List analyses, optionally filtered by event log.
     * @returns AnalysisListResponse Successful Response
     * @throws ApiError
     */
    public static listAnalysesApiV1AnalysesGet({
        datasetId,
        page = 1,
        pageSize = 20,
    }: {
        /**
         * Filter by event log ID
         */
        datasetId?: (string | null),
        page?: number,
        pageSize?: number,
    }): CancelablePromise<AnalysisListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analyses',
            query: {
                'dataset_id': datasetId,
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Analysis
     * Get analysis details with optional full results.
     * @returns AnalysisDetailResponse Successful Response
     * @throws ApiError
     */
    public static getAnalysisApiV1AnalysesAnalysisIdGet({
        analysisId,
        includeResults = true,
    }: {
        analysisId: string,
        /**
         * Include full DFG/variants/statistics
         */
        includeResults?: boolean,
    }): CancelablePromise<AnalysisDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analyses/{analysis_id}',
            path: {
                'analysis_id': analysisId,
            },
            query: {
                'include_results': includeResults,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Analysis
     * Delete an analysis.
     * @returns void
     * @throws ApiError
     */
    public static deleteAnalysisApiV1AnalysesAnalysisIdDelete({
        analysisId,
    }: {
        analysisId: string,
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/analyses/{analysis_id}',
            path: {
                'analysis_id': analysisId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Analyses For Log
     * Get all analyses for a specific event log.
     * @returns AnalysisResponse Successful Response
     * @throws ApiError
     */
    public static listAnalysesForLogApiV1AnalysesLogDatasetIdGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<Array<AnalysisResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/analyses/log/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
