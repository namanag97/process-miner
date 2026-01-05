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
     * @returns PlayOutResponse Successful Response
     * @throws ApiError
     */
    public playOutModelApiV1SimulationModelsModelIdPlayOutPost(
        modelId: string,
        requestBody: PlayOutRequest,
    ): CancelablePromise<PlayOutResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/models/{model_id}/play-out',
            path: {
                'model_id': modelId,
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
     * @param logId
     * @param requestBody
     * @returns SimulationResponse Successful Response
     * @throws ApiError
     */
    public simulateScenarioApiV1SimulationLogsLogIdSimulatePost(
        logId: string,
        requestBody: SimulationRequest,
    ): CancelablePromise<SimulationResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/logs/{log_id}/simulate',
            path: {
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
     * Estimate Capacity
     * Estimate resource requirements for target throughput.
     * @param logId
     * @param targetThroughput
     * @returns any Successful Response
     * @throws ApiError
     */
    public estimateCapacityApiV1SimulationLogsLogIdCapacityPlanPost(
        logId: string,
        targetThroughput: number,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/simulation/logs/{log_id}/capacity-plan',
            path: {
                'log_id': logId,
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
