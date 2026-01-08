/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PlayOutRequest } from '../models/PlayOutRequest';
import type { PlayOutResponse } from '../models/PlayOutResponse';
import type { SimulationRequest } from '../models/SimulationRequest';
import type { SimulationResponse } from '../models/SimulationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class SimulationService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Play Out Model
     * Generate synthetic event log from a process model.
     * @param modelId
     * @param requestBody
     * @param xOrgId
     * @returns PlayOutResponse Successful Response
     * @throws ApiError
     */
    public playOutModelApiV1SimulationModelsModelIdPlayOutPost(
        modelId: string,
        requestBody: PlayOutRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<PlayOutResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/models/{model_id}/play-out',
            path: {
                'model_id': modelId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Simulate Scenario
     * Run what-if simulation on an event log.
     * @param datasetId
     * @param requestBody
     * @param xOrgId
     * @returns SimulationResponse Successful Response
     * @throws ApiError
     */
    public simulateScenarioApiV1SimulationDatasetsDatasetIdSimulatePost(
        datasetId: string,
        requestBody: SimulationRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<SimulationResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/datasets/{dataset_id}/simulate',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Estimate Capacity
     * Estimate resource requirements for target throughput.
     * @param datasetId
     * @param targetThroughput Target throughput
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public estimateCapacityApiV1SimulationDatasetsDatasetIdCapacityPlanPost(
        datasetId: string,
        targetThroughput: number,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/datasets/{dataset_id}/capacity-plan',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'target_throughput': targetThroughput,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
