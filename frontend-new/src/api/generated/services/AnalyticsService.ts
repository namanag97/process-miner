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
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AnalyticsService {
    /**
     * Get Bottlenecks
     * Detect process bottlenecks based on waiting times.
     * @returns BottleneckListResponse Successful Response
     * @throws ApiError
     */
    public static getBottlenecksApiV1AnalyticsDatasetsDatasetIdBottlenecksGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<BottleneckListResponse> {
        return __request(OpenAPI, {
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
     * @returns ReworkListResponse Successful Response
     * @throws ApiError
     */
    public static getReworkApiV1AnalyticsDatasetsDatasetIdReworkGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<ReworkListResponse> {
        return __request(OpenAPI, {
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
     * @returns ServiceTimeResponse Successful Response
     * @throws ApiError
     */
    public static getServiceTimesApiV1AnalyticsDatasetsDatasetIdServiceTimesGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<Array<ServiceTimeResponse>> {
        return __request(OpenAPI, {
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
     * @returns CycleTimeResponse Successful Response
     * @throws ApiError
     */
    public static getCycleTimeApiV1AnalyticsDatasetsDatasetIdCycleTimeGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<CycleTimeResponse> {
        return __request(OpenAPI, {
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
     * @returns ThroughputResponse Successful Response
     * @throws ApiError
     */
    public static getThroughputApiV1AnalyticsDatasetsDatasetIdThroughputGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<ThroughputResponse> {
        return __request(OpenAPI, {
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
     * @returns PatternResponse Successful Response
     * @throws ApiError
     */
    public static getPatternsApiV1AnalyticsDatasetsDatasetIdPatternsGet({
        datasetId,
        minSupport = 0.1,
    }: {
        datasetId: string,
        minSupport?: number,
    }): CancelablePromise<Array<PatternResponse>> {
        return __request(OpenAPI, {
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
     * @returns ReworkChainListResponse Successful Response
     * @throws ApiError
     */
    public static getReworkChainsApiV1AnalyticsDatasetsDatasetIdReworkChainsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<ReworkChainListResponse> {
        return __request(OpenAPI, {
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
     * @returns PerformanceDashboardResponse Successful Response
     * @throws ApiError
     */
    public static getPerformanceDashboardApiV1AnalyticsDatasetsDatasetIdPerformanceGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<PerformanceDashboardResponse> {
        return __request(OpenAPI, {
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
