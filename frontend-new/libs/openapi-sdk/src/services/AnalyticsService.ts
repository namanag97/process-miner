/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalyticsVariantListResponse } from '../models/AnalyticsVariantListResponse';
import type { BottleneckListResponse } from '../models/BottleneckListResponse';
import type { CycleTimeResponse } from '../models/CycleTimeResponse';
import type { ReworkListResponse } from '../models/ReworkListResponse';
import type { ThroughputResponse } from '../models/ThroughputResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AnalyticsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Bottlenecks
     * Detect process bottlenecks based on waiting times.
     *
     * Uses CQRS QueryBus to dispatch GetBottlenecksQuery.
     * Query handler uses DuckDB on Parquet for OLAP performance.
     * @param datasetId
     * @param limit
     * @param xOrgId
     * @returns BottleneckListResponse Successful Response
     * @throws ApiError
     */
    public getBottlenecksApiV1AnalyticsDatasetsDatasetIdBottlenecksGet(
        datasetId: string,
        limit: number = 10,
        xOrgId?: (string | null),
    ): CancelablePromise<BottleneckListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/bottlenecks',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Cycle Time
     * Get cycle time (case duration) statistics.
     *
     * Uses CQRS QueryBus to dispatch GetCycleTimeQuery.
     * @param datasetId
     * @param xOrgId
     * @returns CycleTimeResponse Successful Response
     * @throws ApiError
     */
    public getCycleTimeApiV1AnalyticsDatasetsDatasetIdCycleTimeGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<CycleTimeResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/cycle-time',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Throughput
     * Get throughput statistics for a dataset.
     *
     * Uses CQRS QueryBus to dispatch GetThroughputQuery.
     * @param datasetId
     * @param xOrgId
     * @returns ThroughputResponse Successful Response
     * @throws ApiError
     */
    public getThroughputApiV1AnalyticsDatasetsDatasetIdThroughputGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ThroughputResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/throughput',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Rework
     * Analyze rework (repeated activities) in cases.
     *
     * Uses CQRS QueryBus to dispatch GetReworkQuery.
     * @param datasetId
     * @param xOrgId
     * @returns ReworkListResponse Successful Response
     * @throws ApiError
     */
    public getReworkApiV1AnalyticsDatasetsDatasetIdReworkGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ReworkListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/rework',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Variants
     * Get process variants (unique activity sequences).
     *
     * Uses CQRS QueryBus to dispatch GetVariantsQuery.
     * Returns simplified variant data for analytics dashboards.
     *
     * Note: For detailed variant exploration, use GET /datasets/{id}/variants instead.
     * @param datasetId
     * @param topN
     * @param xOrgId
     * @returns AnalyticsVariantListResponse Successful Response
     * @throws ApiError
     */
    public getVariantsApiV1AnalyticsDatasetsDatasetIdVariantsGet(
        datasetId: string,
        topN: number = 20,
        xOrgId?: (string | null),
    ): CancelablePromise<AnalyticsVariantListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/variants',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'top_n': topN,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
