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
     * @param datasetId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getHandoverNetworkApiV1OrganizationalDatasetsDatasetIdHandoverNetworkGet(
        datasetId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/handover-network',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Collaboration Network
     * Discover working together network.
     * @param datasetId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getCollaborationNetworkApiV1OrganizationalDatasetsDatasetIdCollaborationNetworkGet(
        datasetId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/collaboration-network',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Resource Similarity
     * Discover resource similarity based on activities.
     * @param datasetId
     * @returns SocialNetworkResponse Successful Response
     * @throws ApiError
     */
    public getResourceSimilarityApiV1OrganizationalDatasetsDatasetIdResourceSimilarityGet(
        datasetId: string,
    ): CancelablePromise<SocialNetworkResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/resource-similarity',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Roles
     * Discover organizational roles.
     * @param datasetId
     * @returns ResourceRoleResponse Successful Response
     * @throws ApiError
     */
    public getRolesApiV1OrganizationalDatasetsDatasetIdRolesGet(
        datasetId: string,
    ): CancelablePromise<Array<ResourceRoleResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/roles',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Resource Profile
     * Get detailed profile for a specific resource.
     * @param datasetId
     * @param resource
     * @returns ResourceProfileResponse Successful Response
     * @throws ApiError
     */
    public getResourceProfileApiV1OrganizationalDatasetsDatasetIdResourcesResourceProfileGet(
        datasetId: string,
        resource: string,
    ): CancelablePromise<ResourceProfileResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/resources/{resource}/profile',
            path: {
                'dataset_id': datasetId,
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
     * @param datasetId
     * @returns ResourceWorkloadResponse Successful Response
     * @throws ApiError
     */
    public getWorkloadApiV1OrganizationalDatasetsDatasetIdWorkloadGet(
        datasetId: string,
    ): CancelablePromise<ResourceWorkloadResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/organizational/datasets/{dataset_id}/workload',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
