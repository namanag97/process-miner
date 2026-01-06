/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_dataset_api_v1_datasets__post } from '../models/Body_upload_dataset_api_v1_datasets__post';
import type { ColumnDetectionResponse } from '../models/ColumnDetectionResponse';
import type { DatasetDetailResponse } from '../models/DatasetDetailResponse';
import type { DatasetListResponse } from '../models/DatasetListResponse';
import type { DatasetResponse } from '../models/DatasetResponse';
import type { DownloadResponse } from '../models/DownloadResponse';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { MappingResponse } from '../models/MappingResponse';
import type { MappingUpdateRequest } from '../models/MappingUpdateRequest';
import type { PresignedUploadRequest } from '../models/PresignedUploadRequest';
import type { PresignedUploadResponse } from '../models/PresignedUploadResponse';
import type { PreviewResponse } from '../models/PreviewResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DatasetsService {
    /**
     * List Datasets
     * List all datasets with pagination and filtering.
     * @returns DatasetListResponse Successful Response
     * @throws ApiError
     */
    public static listDatasetsApiV1DatasetsGet({
        page = 1,
        pageSize = 20,
        sourceFormat,
        projectId,
        status,
        xOrgId,
    }: {
        page?: number,
        pageSize?: number,
        sourceFormat?: (string | null),
        projectId?: (string | null),
        /**
         * Filter by status
         */
        status?: (string | null),
        xOrgId?: (string | null),
    }): CancelablePromise<DatasetListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'source_format': sourceFormat,
                'project_id': projectId,
                'status': status,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload Event Log File
     * Upload and store an event log file (CSV or XES).
     *
     * For small files (< 50MB), use this direct upload.
     * For large files (> 50MB), use the presigned upload flow.
     *
     * ## Flow
     * 1. File is validated and stored
     * 2. Validation job is queued automatically
     * 3. Poll `GET /datasets/{id}` for status updates
     * @returns DatasetResponse Dataset created and validation queued
     * @throws ApiError
     */
    public static uploadDatasetApiV1DatasetsPost({
        formData,
        xOrgId,
    }: {
        formData: Body_upload_dataset_api_v1_datasets__post,
        xOrgId?: (string | null),
    }): CancelablePromise<DatasetResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/',
            headers: {
                'X-Org-Id': xOrgId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Invalid file format`,
                413: `File too large (> 100MB)`,
                422: `Validation error`,
            },
        });
    }
    /**
     * Get Dataset Details
     * Get detailed information about a dataset.
     * @returns DatasetDetailResponse Successful Response
     * @throws ApiError
     */
    public static getDatasetApiV1DatasetsDatasetIdGet({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<DatasetDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Dataset
     * Delete a dataset and all associated data.
     * @returns any Dataset deleted
     * @throws ApiError
     */
    public static deleteDatasetApiV1DatasetsDatasetIdDelete({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/datasets/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Dataset Sheets
     * Get list of sheets for multi-sheet files (Excel). CSV/XES files return a single sheet.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDatasetSheetsApiV1DatasetsDatasetIdSheetsGet({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/sheets',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Presigned S3 Upload URL
     * Generate a presigned URL for direct S3 upload.
     *
     * ## Flow
     * 1. Call this endpoint to get `upload_url`
     * 2. PUT the file to `upload_url`
     * 3. Call `POST /datasets/{id}/uploaded` to trigger validation
     * @returns PresignedUploadResponse Presigned URL generated successfully
     * @throws ApiError
     */
    public static createPresignedUploadApiV1DatasetsPresignPost({
        requestBody,
        xOrgId,
    }: {
        requestBody: PresignedUploadRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<PresignedUploadResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/presign',
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation error (invalid extension)`,
                429: `Rate limit exceeded (10/min)`,
            },
        });
    }
    /**
     * Confirm Upload Complete
     * Confirm that S3 upload is complete and trigger validation.
     *
     * Call this after successfully uploading to the presigned URL.
     * @returns any Validation queued
     * @throws ApiError
     */
    public static confirmUploadCompleteApiV1DatasetsDatasetIdUploadedPost({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/uploaded',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                400: `Dataset not in PENDING state`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Detected Columns
     * Get detected columns with type information and mapping suggestions.
     *
     * Returns each column with:
     * - Detected data type
     * - Sample values
     * - Suggested role (case_id, activity, timestamp, resource)
     * - Confidence score for suggestion ( 0.0-1.0)
     * @returns ColumnDetectionResponse Column detection results
     * @throws ApiError
     */
    public static getColumnsApiV1DatasetsDatasetIdColumnsGet({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<ColumnDetectionResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/columns',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Submit Column Mapping
     * Submit column mapping for the dataset.
     *
     * Required mappings:
     * - case_id_column: Column containing case/trace identifiers
     * - activity_column: Column containing activity names
     * - timestamp_column: Column containing event timestamps
     *
     * Optional mappings:
     * - resource_column: Column containing performer/resource
     * - timestamp_format: Timestamp format string (auto-detected if not provided)
     * @returns any Mapping saved, status → MAPPED
     * @throws ApiError
     */
    public static submitMappingApiV1DatasetsDatasetIdMappingPost({
        datasetId,
        requestBody,
        xOrgId,
    }: {
        datasetId: string,
        requestBody: MappingUpdateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/mapping',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid mapping (column not found)`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current Mapping
     * Get the current column mapping for a dataset.
     * @returns MappingResponse Current mapping
     * @throws ApiError
     */
    public static getMappingApiV1DatasetsDatasetIdMappingGet({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<MappingResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/mapping',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                404: `Dataset or mapping not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Mapping
     * Update the column mapping for a dataset.
     * @returns MappingResponse Mapping updated
     * @throws ApiError
     */
    public static updateMappingApiV1DatasetsDatasetIdMappingPut({
        datasetId,
        requestBody,
        xOrgId,
    }: {
        datasetId: string,
        requestBody: MappingUpdateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<MappingResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/datasets/{dataset_id}/mapping',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Invalid mapping`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Preview Mapped Data
     * Preview how data will look after applying the mapping.
     *
     * Returns a sample of events with the mapping applied.
     * Useful for verifying column selections before ingestion.
     * @returns PreviewResponse Preview generated
     * @throws ApiError
     */
    public static previewMappedDataApiV1DatasetsDatasetIdPreviewPost({
        datasetId,
        limit = 10,
        xOrgId,
    }: {
        datasetId: string,
        /**
         * Number of sample rows
         */
        limit?: number,
        xOrgId?: (string | null),
    }): CancelablePromise<PreviewResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/preview',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'limit': limit,
            },
            errors: {
                400: `No mapping found`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Trigger Dataset Ingestion
     * Start background ingestion job for a MAPPED dataset.
     *
     * Prerequisites:
     * - Dataset must be in MAPPED status
     * - Column mapping must be saved
     *
     * The ingestion job will:
     * 1. Parse the file using the column mapping
     * 2. Insert events into process_events table
     * 3. Aggregate into process_cases
     * 4. Compute metadata statistics
     * 5. Update status to READY
     *
     * Use `GET /jobs/{job_id}` to track progress.
     * @returns JobStatusResponse Successful Response
     * @returns any Ingestion job queued
     * @throws ApiError
     */
    public static triggerIngestionApiV1DatasetsDatasetIdIngestPost({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<JobStatusResponse | any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/ingest',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                400: `Dataset not in MAPPED state`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Re-ingest Dataset
     * Re-ingest a dataset with updated mapping.
     *
     * Use this when you've updated the column mapping and want to
     * re-process the data without re-uploading the file.
     *
     * Clears existing events and reprocesses from the original file.
     * @returns JobStatusResponse Successful Response
     * @returns any Re-ingestion job queued
     * @throws ApiError
     */
    public static triggerReingestApiV1DatasetsDatasetIdReingestPost({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<JobStatusResponse | any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/reingest',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                400: `Dataset not in READY or ERROR state`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Export Dataset
     * Export dataset to specified format (async job).
     *
     * Supported formats:
     * - csv: Standard CSV file
     * - xes: XES format for process mining tools
     * - parquet: Columnar format for big data tools
     *
     * Returns job ID to track export progress.
     * @returns JobStatusResponse Successful Response
     * @returns any Export job queued
     * @throws ApiError
     */
    public static exportDatasetApiV1DatasetsDatasetIdExportPost({
        datasetId,
        exportFormat = 'csv',
        xOrgId,
    }: {
        datasetId: string,
        exportFormat?: string,
        xOrgId?: (string | null),
    }): CancelablePromise<JobStatusResponse | any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/export',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'export_format': exportFormat,
            },
            errors: {
                400: `Invalid format or dataset not ready`,
                404: `Dataset not found`,
                422: `Validation Error`,
            },
        });
    }
    /**
     * Download Original File
     * Get presigned URL to download the original uploaded file.
     *
     * Returns a temporary URL that expires after 1 hour.
     * @returns DownloadResponse Download URL generated
     * @throws ApiError
     */
    public static downloadOriginalFileApiV1DatasetsDatasetIdDownloadGet({
        datasetId,
        xOrgId,
    }: {
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<DownloadResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/download',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                404: `Dataset or file not found`,
                422: `Validation Error`,
            },
        });
    }
}
