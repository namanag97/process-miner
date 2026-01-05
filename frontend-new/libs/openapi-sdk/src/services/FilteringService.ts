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
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class FilteringService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Apply Filters
     * Apply filters to an event log and create a new filtered log.
     *
     * This creates a new event log that is a filtered version of the source log.
     * The original log is not modified.
     * @param datasetId
     * @param requestBody
     * @returns FilteredLogResponse Successful Response
     * @throws ApiError
     */
    public applyFiltersApiV1FilteringDatasetsDatasetIdApplyPost(
        datasetId: string,
        requestBody: FilterRequest,
    ): CancelablePromise<FilteredLogResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param requestBody
     * @returns FilterPreviewResponse Successful Response
     * @throws ApiError
     */
    public previewFiltersApiV1FilteringDatasetsDatasetIdPreviewPost(
        datasetId: string,
        requestBody: FilterPreviewRequest,
    ): CancelablePromise<FilterPreviewResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @returns FilterOptionsResponse Successful Response
     * @throws ApiError
     */
    public getFilterOptionsApiV1FilteringDatasetsDatasetIdOptionsGet(
        datasetId: string,
    ): CancelablePromise<FilterOptionsResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @returns FilteredLogListResponse Successful Response
     * @throws ApiError
     */
    public listFilteredLogsApiV1FilteringDatasetsDatasetIdResultsGet(
        datasetId: string,
    ): CancelablePromise<FilteredLogListResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param filteredId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteFilteredLogApiV1FilteringDatasetsDatasetIdResultsFilteredIdDelete(
        datasetId: string,
        filteredId: string,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
    public getFilterTemplatesApiV1FilteringTemplatesGet(): CancelablePromise<FilterTemplateListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/filtering/templates',
        });
    }
}
