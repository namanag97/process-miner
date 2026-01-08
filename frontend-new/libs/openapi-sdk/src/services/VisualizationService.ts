/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DFGResponse } from '../models/DFGResponse';
import type { PetriNetResponse } from '../models/PetriNetResponse';
import type { ProcessExplorerDataResponse } from '../models/ProcessExplorerDataResponse';
import type { TieredDFGResponse } from '../models/TieredDFGResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class VisualizationService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
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
     * @param datasetId
     * @param includePerformance Include performance metrics (avg/min/max duration) for edges
     * @returns DFGResponse Successful Response
     * @throws ApiError
     */
    public getDfgApiV1VisualizationDatasetIdDfgGet(
        datasetId: string,
        includePerformance: boolean = false,
    ): CancelablePromise<DFGResponse> {
        return this.httpRequest.request({
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
     * Get Tiered Dfg
     * Get tiered DFG data for progressive loading performance.
     *
     * This endpoint supports three typical configurations:
     * - **Overview tier**: max_nodes=50, min_edge_frequency=100, aggregate=true
     * Fast initial load with top activities and high-frequency paths
     * - **Standard tier**: max_nodes=500, min_edge_frequency=10, aggregate=false
     * Balanced view with most activities visible
     * - **Detailed tier**: max_nodes=null, min_edge_frequency=1, aggregate=false
     * Full graph with all nodes and edges
     *
     * The response includes metadata about the full graph size, allowing
     * the frontend to show "X of Y nodes" and offer tier upgrades.
     *
     * ## Performance Benefits
     * - Overview tier typically returns in <50ms for any graph size
     * - Enables fast initial render with progressive enhancement
     * - Reduces memory usage on frontend for large graphs
     * @param datasetId
     * @param maxNodes Maximum nodes to return (null for all)
     * @param minEdgeFrequency Minimum edge frequency to include
     * @param aggregate Aggregate low-frequency nodes into 'Other' cluster
     * @param includePerformance Include performance metrics on edges
     * @returns TieredDFGResponse Successful Response
     * @throws ApiError
     */
    public getTieredDfgApiV1VisualizationDatasetIdDfgTieredGet(
        datasetId: string,
        maxNodes?: (number | null),
        minEdgeFrequency: number = 1,
        aggregate: boolean = true,
        includePerformance: boolean = false,
    ): CancelablePromise<TieredDFGResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/visualization/{dataset_id}/dfg/tiered',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'max_nodes': maxNodes,
                'min_edge_frequency': minEdgeFrequency,
                'aggregate': aggregate,
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
     * @param modelId
     * @returns PetriNetResponse Successful Response
     * @throws ApiError
     */
    public getPetriNetApiV1VisualizationModelsModelIdPetriGet(
        modelId: string,
    ): CancelablePromise<PetriNetResponse> {
        return this.httpRequest.request({
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
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getModelSvgApiV1VisualizationModelsModelIdSvgGet(
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDfgSvgApiV1VisualizationDatasetIdDfgSvgGet(
        datasetId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getFootprintsApiV1VisualizationDatasetIdFootprintsGet(
        datasetId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param includePerformance Include performance metrics in DFG edges
     * @param includeComplexity Include complexity metrics in variants
     * @param topVariants Number of top variants to include
     * @returns ProcessExplorerDataResponse Successful Response
     * @throws ApiError
     */
    public getExplorerDataApiV1VisualizationDatasetIdExplorerDataGet(
        datasetId: string,
        includePerformance: boolean = true,
        includeComplexity: boolean = true,
        topVariants: number = 20,
    ): CancelablePromise<ProcessExplorerDataResponse> {
        return this.httpRequest.request({
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
