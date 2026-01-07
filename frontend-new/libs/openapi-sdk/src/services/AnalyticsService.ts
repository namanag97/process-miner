/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BottleneckListResponse } from '../models/BottleneckListResponse';
import type { CycleTimeResponse } from '../models/CycleTimeResponse';
import type { PatternResponse } from '../models/PatternResponse';
import type { PerformanceDashboardResponse } from '../models/PerformanceDashboardResponse';
import type { ReworkChainListResponse } from '../models/ReworkChainListResponse';
import type { ReworkListResponse } from '../models/ReworkListResponse';
import type { ServiceTimeResponse } from '../models/ServiceTimeResponse';
import type { ThroughputResponse } from '../models/ThroughputResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AnalyticsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Bottlenecks
     * Detect process bottlenecks based on waiting times.
     * @param datasetId
     * @returns BottleneckListResponse Successful Response
     * @throws ApiError
     */
    public getBottlenecksApiV1AnalyticsDatasetsDatasetIdBottlenecksGet(
        datasetId: string,
    ): CancelablePromise<BottleneckListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/bottlenecks',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Rework
     * Analyze rework (repeated activities) in cases.
     * @param datasetId
     * @returns ReworkListResponse Successful Response
     * @throws ApiError
     */
    public getReworkApiV1AnalyticsDatasetsDatasetIdReworkGet(
        datasetId: string,
    ): CancelablePromise<ReworkListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/rework',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Service Times
     * Get service time statistics per activity.
     * @param datasetId
     * @returns ServiceTimeResponse Successful Response
     * @throws ApiError
     */
    public getServiceTimesApiV1AnalyticsDatasetsDatasetIdServiceTimesGet(
        datasetId: string,
    ): CancelablePromise<Array<ServiceTimeResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/service-times',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Cycle Time
     * Get cycle time (case duration) statistics.
     * @param datasetId
     * @returns CycleTimeResponse Successful Response
     * @throws ApiError
     */
    public getCycleTimeApiV1AnalyticsDatasetsDatasetIdCycleTimeGet(
        datasetId: string,
    ): CancelablePromise<CycleTimeResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/cycle-time',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Throughput
     * Get throughput metrics (cases per day/week/month).
     * @param datasetId
     * @returns ThroughputResponse Successful Response
     * @throws ApiError
     */
    public getThroughputApiV1AnalyticsDatasetsDatasetIdThroughputGet(
        datasetId: string,
    ): CancelablePromise<ThroughputResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/throughput',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Patterns
     * Get frequent activity patterns/subsequences.
     * @param datasetId
     * @param minSupport
     * @returns PatternResponse Successful Response
     * @throws ApiError
     */
    public getPatternsApiV1AnalyticsDatasetsDatasetIdPatternsGet(
        datasetId: string,
        minSupport: number = 0.1,
    ): CancelablePromise<Array<PatternResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/patterns',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'min_support': minSupport,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Rework Chains
     * Detect rework chains - consecutive repetitions of the same activity.
     *
     * A rework chain is when an activity appears multiple times consecutively,
     * indicating immediate rework/retry patterns. For example, if activity 'Review'
     * appears 3 times in a row, that's a chain of length 3.
     *
     * Returns:
     * - chains: List of detected rework chains with frequency and duration
     * - most_problematic_activity: Activity with the most chains
     * - cases_with_chains: Number of cases containing chains
     * @param datasetId
     * @returns ReworkChainListResponse Successful Response
     * @throws ApiError
     */
    public getReworkChainsApiV1AnalyticsDatasetsDatasetIdReworkChainsGet(
        datasetId: string,
    ): CancelablePromise<ReworkChainListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/rework-chains',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Performance Dashboard
     * Get comprehensive performance dashboard.
     * @param datasetId
     * @returns PerformanceDashboardResponse Successful Response
     * @throws ApiError
     */
    public getPerformanceDashboardApiV1AnalyticsDatasetsDatasetIdPerformanceGet(
        datasetId: string,
    ): CancelablePromise<PerformanceDashboardResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/analytics/datasets/{dataset_id}/performance',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
