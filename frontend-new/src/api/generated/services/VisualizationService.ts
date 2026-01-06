/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DFGResponse } from '../models/DFGResponse';
import type { PetriNetResponse } from '../models/PetriNetResponse';
import type { ProcessExplorerDataResponse } from '../models/ProcessExplorerDataResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VisualizationService {
    /**
     * Get Dfg
     * Get Directly-Follows Graph data for visualization.
     *
     * Returns nodes (activities) and edges (transitions) with frequencies,
     * optimized for rendering with React Flow, D3, or similar libraries.
     *
     * When include_performance=true, edges include timing metrics:
     * - avg_duration_seconds: Mean time between activities
     * - min_duration_seconds: Minimum time between activities
     * - max_duration_seconds: Maximum time between activities
     * @returns DFGResponse Successful Response
     * @throws ApiError
     */
    public static getDfgApiV1VisualizationDatasetIdDfgGet({
        datasetId,
        includePerformance = false,
    }: {
        datasetId: string,
        /**
         * Include performance metrics (avg/min/max duration) for edges
         */
        includePerformance?: boolean,
    }): CancelablePromise<DFGResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/{dataset_id}/dfg',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'include_performance': includePerformance,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Petri Net
     * Get Petri net structure for visualization.
     *
     * Returns places, transitions, and arcs with initial/final markings.
     * Works with models discovered using Alpha, Heuristics, or Inductive miners.
     * @returns PetriNetResponse Successful Response
     * @throws ApiError
     */
    public static getPetriNetApiV1VisualizationModelsModelIdPetriGet({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<PetriNetResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/models/{model_id}/petri',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Model Svg
     * Get SVG visualization of a process model.
     *
     * Returns an SVG image that can be displayed directly in the browser.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getModelSvgApiV1VisualizationModelsModelIdSvgGet({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/models/{model_id}/svg',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Dfg Svg
     * Get SVG visualization of DFG for an event log.
     *
     * Discovers DFG and returns SVG visualization.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDfgSvgApiV1VisualizationDatasetIdDfgSvgGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/{dataset_id}/dfg/svg',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Footprints
     * Get behavioral footprints for an event log.
     *
     * Shows sequence and parallel relations between activities.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getFootprintsApiV1VisualizationDatasetIdFootprintsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/{dataset_id}/footprints',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Explorer Data
     * Get unified explorer data for the Process Explorer frontend component.
     *
     * Returns all data needed for the process explorer in a single request:
     * - dfg: Directly-Follows Graph with nodes and edges
     * - variants: Top process variants with optional complexity metrics
     * - activities: Activity statistics with frequency and timing
     * - statistics: Overall process statistics
     *
     * This endpoint is optimized for the frontend to reduce API calls.
     * @returns ProcessExplorerDataResponse Successful Response
     * @throws ApiError
     */
    public static getExplorerDataApiV1VisualizationDatasetIdExplorerDataGet({
        datasetId,
        includePerformance = true,
        includeComplexity = true,
        topVariants = 20,
    }: {
        datasetId: string,
        /**
         * Include performance metrics in DFG edges
         */
        includePerformance?: boolean,
        /**
         * Include complexity metrics in variants
         */
        includeComplexity?: boolean,
        /**
         * Number of top variants to include
         */
        topVariants?: number,
    }): CancelablePromise<ProcessExplorerDataResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/visualization/{dataset_id}/explorer-data',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'include_performance': includePerformance,
                'include_complexity': includeComplexity,
                'top_variants': topVariants,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
