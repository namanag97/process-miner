/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FilteredLogListResponse } from '../models/FilteredLogListResponse';
import type { FilteredLogResponse } from '../models/FilteredLogResponse';
import type { FilterOptionsResponse } from '../models/FilterOptionsResponse';
import type { FilterPreviewRequest } from '../models/FilterPreviewRequest';
import type { FilterPreviewResponse } from '../models/FilterPreviewResponse';
import type { FilterRequest } from '../models/FilterRequest';
import type { FilterTemplateListResponse } from '../models/FilterTemplateListResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class FilteringService {
    /**
     * Apply Filters
     * Apply filters to an event log and create a new filtered log.
     *
     * This creates a new event log that is a filtered version of the source log.
     * The original log is not modified.
     * @returns FilteredLogResponse Successful Response
     * @throws ApiError
     */
    public static applyFiltersApiV1FilteringDatasetsDatasetIdApplyPost({
        datasetId,
        requestBody,
    }: {
        datasetId: string,
        requestBody: FilterRequest,
    }): CancelablePromise<FilteredLogResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/filtering/datasets/{dataset_id}/apply',
            path: {
                'dataset_id': datasetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Preview Filters
     * Preview the impact of filters without saving.
     *
     * Returns statistics on how many cases/events would be retained.
     * @returns FilterPreviewResponse Successful Response
     * @throws ApiError
     */
    public static previewFiltersApiV1FilteringDatasetsDatasetIdPreviewPost({
        datasetId,
        requestBody,
    }: {
        datasetId: string,
        requestBody: FilterPreviewRequest,
    }): CancelablePromise<FilterPreviewResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/filtering/datasets/{dataset_id}/preview',
            path: {
                'dataset_id': datasetId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Filter Options
     * Get available filter options based on log contents.
     *
     * Returns activities, resources, time ranges, and other values
     * that can be used for filtering.
     * @returns FilterOptionsResponse Successful Response
     * @throws ApiError
     */
    public static getFilterOptionsApiV1FilteringDatasetsDatasetIdOptionsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<FilterOptionsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/filtering/datasets/{dataset_id}/options',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Filtered Logs
     * List all filtered versions of an event log.
     * @returns FilteredLogListResponse Successful Response
     * @throws ApiError
     */
    public static listFilteredLogsApiV1FilteringDatasetsDatasetIdResultsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<FilteredLogListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/filtering/datasets/{dataset_id}/results',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Filtered Log
     * Delete a filtered log.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteFilteredLogApiV1FilteringDatasetsDatasetIdResultsFilteredIdDelete({
        datasetId,
        filteredId,
    }: {
        datasetId: string,
        filteredId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/filtering/datasets/{dataset_id}/results/{filtered_id}',
            path: {
                'dataset_id': datasetId,
                'filtered_id': filteredId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Filter Templates
     * Get pre-built filter templates.
     * @returns FilterTemplateListResponse Successful Response
     * @throws ApiError
     */
    public static getFilterTemplatesApiV1FilteringTemplatesGet(): CancelablePromise<FilterTemplateListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/filtering/templates',
        });
    }
}
