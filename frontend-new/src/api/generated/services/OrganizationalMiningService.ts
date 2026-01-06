/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ResourceProfileResponse } from '../models/ResourceProfileResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OrganizationalMiningService {
    /**
     * Get Resource Profile
     * Get detailed profile for a specific resource.
     * @returns ResourceProfileResponse Successful Response
     * @throws ApiError
     */
    public static getResourceProfileApiV1OrganizationalDatasetsDatasetIdResourcesResourceProfileGet({
        datasetId,
        resource,
    }: {
        datasetId: string,
        resource: string,
    }): CancelablePromise<ResourceProfileResponse> {
        return __request(OpenAPI, {
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
}
