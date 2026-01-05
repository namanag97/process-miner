/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalysisCreateRequest } from '../models/AnalysisCreateRequest';
import type { AnalysisDetailResponse } from '../models/AnalysisDetailResponse';
import type { AnalysisListResponse } from '../models/AnalysisListResponse';
import type { AnalysisResponse } from '../models/AnalysisResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AnalysesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
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
    public getAnalysisMetadataApiV1AnalysesMetadataGet(): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analyses/metadata',
        });
    }
    /**
     * Create Analysis
     * Create a new analysis for an event log.
     *
     * The analysis will be queued for processing and status updated when complete.
     * @param logId
     * @param requestBody
     * @returns AnalysisResponse Successful Response
     * @throws ApiError
     */
    public createAnalysisApiV1AnalysesPost(
        logId: string,
        requestBody: AnalysisCreateRequest,
    ): CancelablePromise<AnalysisResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/analyses',
            query: {
                'log_id': logId,
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
     * @param logId Filter by event log ID
     * @param page
     * @param pageSize
     * @returns AnalysisListResponse Successful Response
     * @throws ApiError
     */
    public listAnalysesApiV1AnalysesGet(
        logId?: (string | null),
        page: number = 1,
        pageSize: number = 20,
    ): CancelablePromise<AnalysisListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analyses',
            query: {
                'log_id': logId,
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
     * @param analysisId
     * @param includeResults Include full DFG/variants/statistics
     * @returns AnalysisDetailResponse Successful Response
     * @throws ApiError
     */
    public getAnalysisApiV1AnalysesAnalysisIdGet(
        analysisId: string,
        includeResults: boolean = true,
    ): CancelablePromise<AnalysisDetailResponse> {
        return this.httpRequest.request({
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
     * @param analysisId
     * @returns void
     * @throws ApiError
     */
    public deleteAnalysisApiV1AnalysesAnalysisIdDelete(
        analysisId: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
     * @param logId
     * @returns AnalysisResponse Successful Response
     * @throws ApiError
     */
    public listAnalysesForLogApiV1AnalysesLogLogIdGet(
        logId: string,
    ): CancelablePromise<Array<AnalysisResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analyses/log/{log_id}',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
