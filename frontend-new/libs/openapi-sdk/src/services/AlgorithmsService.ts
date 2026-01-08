/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AlgorithmsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Algorithms
     * List all available mining algorithms with metadata.
     *
     * Returns algorithms sorted by display order with:
     * - Speed and noise tolerance ratings
     * - Recommended event/activity limits
     * - Soundness guarantees
     * - External dependency requirements
     * @param category Filter by category (discovery, conformance, declarative, enhancement)
     * @param includeDisabled Include disabled algorithms
     * @returns any Successful Response
     * @throws ApiError
     */
    public listAlgorithmsApiV1AlgorithmsGet(
        category?: (string | null),
        includeDisabled: boolean = false,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/algorithms',
            query: {
                'category': category,
                'include_disabled': includeDisabled,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Recommend Algorithm
     * Get algorithm recommendation based on dataset characteristics.
     *
     * Analyzes the dataset's:
     * - Event count
     * - Activity count
     * - Variant ratio
     *
     * Returns a primary recommendation with alternatives and reasoning.
     * @param datasetId Dataset to analyze for recommendation
     * @param useCase Optimization goal: quick, quality, noisy, declarative
     * @returns any Successful Response
     * @throws ApiError
     */
    public recommendAlgorithmApiV1AlgorithmsRecommendGet(
        datasetId: string,
        useCase?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/algorithms/recommend',
            query: {
                'dataset_id': datasetId,
                'use_case': useCase,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Algorithm
     * Get detailed information about a specific algorithm.
     *
     * Returns:
     * - Full metadata
     * - All configurable parameters with types, ranges, defaults
     * - Parameter descriptions for UI tooltips
     * @param algorithmId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAlgorithmApiV1AlgorithmsAlgorithmIdGet(
        algorithmId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/algorithms/{algorithm_id}',
            path: {
                'algorithm_id': algorithmId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Algorithm Parameters
     * Get parameters for a specific algorithm.
     *
     * Useful for building dynamic parameter forms in the UI.
     * @param algorithmId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAlgorithmParametersApiV1AlgorithmsAlgorithmIdParametersGet(
        algorithmId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/algorithms/{algorithm_id}/parameters',
            path: {
                'algorithm_id': algorithmId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
