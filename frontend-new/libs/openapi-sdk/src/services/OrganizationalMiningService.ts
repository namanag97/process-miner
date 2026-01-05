/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceProfileResponse } from '../models/ResourceProfileResponse';
import type { ResourceRoleResponse } from '../models/ResourceRoleResponse';
import type { ResourceWorkloadResponse } from '../models/ResourceWorkloadResponse';
import type { SocialNetworkResponse } from '../models/SocialNetworkResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class OrganizationalMiningService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Handover Network
     * Discover handover of work network.
     * @param logId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getHandoverNetworkApiV1OrganizationalLogsLogIdHandoverNetworkGet(
        logId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/handover-network',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Collaboration Network
     * Discover working together network.
     * @param logId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getCollaborationNetworkApiV1OrganizationalLogsLogIdCollaborationNetworkGet(
        logId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/collaboration-network',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Resource Similarity
     * Discover resource similarity based on activities.
     * @param logId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getResourceSimilarityApiV1OrganizationalLogsLogIdResourceSimilarityGet(
        logId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/resource-similarity',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Roles
     * Discover organizational roles.
     * @param logId
     * @returns ResourceRoleResponse Successful Response
     * @throws ApiError
     */
    public getRolesApiV1OrganizationalLogsLogIdRolesGet(
        logId: string,
    ): CancelablePromise<Array<ResourceRoleResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/roles',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Resource Profile
     * Get detailed profile for a specific resource.
     * @param logId
     * @param resource
     * @returns ResourceProfileResponse Successful Response
     * @throws ApiError
     */
    public getResourceProfileApiV1OrganizationalLogsLogIdResourcesResourceProfileGet(
        logId: string,
        resource: string,
    ): CancelablePromise<ResourceProfileResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/resources/{resource}/profile',
            path: {
                'log_id': logId,
                'resource': resource,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Workload
     * Get workload distribution across resources.
     * @param logId
     * @returns ResourceWorkloadResponse Successful Response
     * @throws ApiError
     */
    public getWorkloadApiV1OrganizationalLogsLogIdWorkloadGet(
        logId: string,
    ): CancelablePromise<ResourceWorkloadResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/logs/{log_id}/workload',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
