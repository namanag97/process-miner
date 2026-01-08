/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityDetailResponse } from '../models/ActivityDetailResponse';
import type { Body_upload_dataset_api_v1_datasets__post } from '../models/Body_upload_dataset_api_v1_datasets__post';
import type { CaseListResponse } from '../models/CaseListResponse';
import type { ColumnDetectionResponse } from '../models/ColumnDetectionResponse';
import type { DatasetDetailResponse } from '../models/DatasetDetailResponse';
import type { DatasetListResponse } from '../models/DatasetListResponse';
import type { DatasetResponse } from '../models/DatasetResponse';
import type { DownloadResponse } from '../models/DownloadResponse';
import type { EventListResponse } from '../models/EventListResponse';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { MappingResponse } from '../models/MappingResponse';
import type { MappingUpdateRequest } from '../models/MappingUpdateRequest';
import type { MetadataResponse } from '../models/MetadataResponse';
import type { PresignedUploadRequest } from '../models/PresignedUploadRequest';
import type { PresignedUploadResponse } from '../models/PresignedUploadResponse';
import type { PreviewResponse } from '../models/PreviewResponse';
import type { StatisticsResponse } from '../models/StatisticsResponse';
import type { VariantResponse } from '../models/VariantResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DatasetsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Datasets
     * List all datasets with pagination and filtering.
     * @param page
     * @param pageSize
     * @param sourceFormat
     * @param projectId
     * @param status Filter by status
     * @param xOrgId
     * @returns DatasetListResponse Successful Response
     * @throws ApiError
     */
    public listDatasetsApiV1DatasetsGet(
        page: number = 1,
        pageSize: number = 20,
        sourceFormat?: (string | null),
        projectId?: (string | null),
        status?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<DatasetListResponse> {
        return this.httpRequest.request({
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
     * @param formData
     * @param xOrgId
     * @returns DatasetResponse Dataset created and validation queued
     * @throws ApiError
     */
    public uploadDatasetApiV1DatasetsPost(
        formData: Body_upload_dataset_api_v1_datasets__post,
        xOrgId?: (string | null),
    ): CancelablePromise<DatasetResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns DatasetDetailResponse Successful Response
     * @throws ApiError
     */
    public getDatasetApiV1DatasetsDatasetIdGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<DatasetDetailResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns any Dataset deleted
     * @throws ApiError
     */
    public deleteDatasetApiV1DatasetsDatasetIdDelete(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDatasetSheetsApiV1DatasetsDatasetIdSheetsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
     * Get Raw Data Preview
     * Get a preview of the raw data from the uploaded file.
     *
     * Returns column information with detected types and sample row data.
     * Used by the upload wizard's Configure step before mapping is applied.
     * @param datasetId
     * @param rows Number of sample rows to return
     * @param xOrgId
     * @returns any Preview data with columns and sample rows
     * @throws ApiError
     */
    public getDatasetPreviewApiV1DatasetsDatasetIdPreviewGet(
        datasetId: string,
        rows: number = 10,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/preview',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'rows': rows,
            },
            errors: {
                404: `Dataset not found or file not accessible`,
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
     * @param datasetId
     * @param limit Number of sample rows
     * @param xOrgId
     * @returns PreviewResponse Preview generated
     * @throws ApiError
     */
    public previewMappedDataApiV1DatasetsDatasetIdPreviewPost(
        datasetId: string,
        limit: number = 10,
        xOrgId?: (string | null),
    ): CancelablePromise<PreviewResponse> {
        return this.httpRequest.request({
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
     * Get Presigned S3 Upload URL
     * Generate a presigned URL for direct S3 upload.
     *
     * ## Flow
     * 1. Call this endpoint to get `upload_url`
     * 2. PUT the file to `upload_url`
     * 3. Call `POST /datasets/{id}/uploaded` to trigger validation
     * @param requestBody
     * @param xOrgId
     * @returns PresignedUploadResponse Presigned URL generated successfully
     * @throws ApiError
     */
    public createPresignedUploadApiV1DatasetsPresignPost(
        requestBody: PresignedUploadRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<PresignedUploadResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns any Validation queued
     * @throws ApiError
     */
    public confirmUploadCompleteApiV1DatasetsDatasetIdUploadedPost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
     * Trigger Column Detection
     * Manually trigger column detection for an existing dataset.
     *
     * Use this when:
     * - Columns were not detected during upload (e.g., Temporal unavailable)
     * - You want to re-detect columns with updated settings
     *
     * Works on datasets in UPLOADED or AWAITING_MAPPING status.
     * @param datasetId
     * @param xOrgId
     * @returns any Column detection completed
     * @throws ApiError
     */
    public validateDatasetApiV1DatasetsDatasetIdValidatePost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/validate',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                400: `Dataset not in valid state`,
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
     * @param datasetId
     * @param xOrgId
     * @returns ColumnDetectionResponse Column detection results
     * @throws ApiError
     */
    public getColumnsApiV1DatasetsDatasetIdColumnsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ColumnDetectionResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param requestBody
     * @param xOrgId
     * @returns any Mapping saved, status → MAPPED
     * @throws ApiError
     */
    public submitMappingApiV1DatasetsDatasetIdMappingPost(
        datasetId: string,
        requestBody: MappingUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns MappingResponse Current mapping
     * @throws ApiError
     */
    public getMappingApiV1DatasetsDatasetIdMappingGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<MappingResponse> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param requestBody
     * @param xOrgId
     * @returns MappingResponse Mapping updated
     * @throws ApiError
     */
    public updateMappingApiV1DatasetsDatasetIdMappingPut(
        datasetId: string,
        requestBody: MappingUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<MappingResponse> {
        return this.httpRequest.request({
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
     * Use `GET /operations/{workflow_id}` to track progress.
     * @param datasetId
     * @param xOrgId
     * @returns JobStatusResponse Successful Response
     * @returns any Ingestion job queued
     * @throws ApiError
     */
    public triggerIngestionApiV1DatasetsDatasetIdIngestPost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<JobStatusResponse | any> {
        return this.httpRequest.request({
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
     * Synchronous Ingestion (Dev Mode)
     * Process dataset ingestion synchronously without Temporal.
     *
     * **Development mode only** - use this when Temporal is unavailable.
     * For production, use `POST /datasets/{id}/ingest` with Temporal workflows.
     *
     * Prerequisites:
     * - Dataset must be in MAPPED or ERROR status
     * - Column mapping must be saved
     * @param datasetId
     * @param xOrgId
     * @returns any Ingestion completed successfully
     * @throws ApiError
     */
    public syncIngestApiV1DatasetsDatasetIdIngestSyncPost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/ingest-sync',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                400: `Dataset not in valid state`,
                404: `Dataset not found`,
                422: `Validation Error`,
                500: `Ingestion failed`,
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
     * @param datasetId
     * @param xOrgId
     * @returns JobStatusResponse Successful Response
     * @returns any Re-ingestion job queued
     * @throws ApiError
     */
    public triggerReingestApiV1DatasetsDatasetIdReingestPost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<JobStatusResponse | any> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param exportFormat
     * @param xOrgId
     * @returns JobStatusResponse Successful Response
     * @returns any Export job queued
     * @throws ApiError
     */
    public exportDatasetApiV1DatasetsDatasetIdExportPost(
        datasetId: string,
        exportFormat: string = 'csv',
        xOrgId?: (string | null),
    ): CancelablePromise<JobStatusResponse | any> {
        return this.httpRequest.request({
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
     * @param datasetId
     * @param xOrgId
     * @returns DownloadResponse Download URL generated
     * @throws ApiError
     */
    public downloadOriginalFileApiV1DatasetsDatasetIdDownloadGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<DownloadResponse> {
        return this.httpRequest.request({
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
    /**
     * Get Dataset Statistics
     * Get comprehensive statistics for a dataset.
     * @param datasetId
     * @param xOrgId
     * @returns StatisticsResponse Successful Response
     * @throws ApiError
     */
    public getStatisticsApiV1DatasetsDatasetIdStatisticsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<StatisticsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/statistics',
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
     * List Cases
     * List cases/traces in a dataset with pagination.
     * @param datasetId
     * @param page
     * @param pageSize
     * @param xOrgId
     * @returns CaseListResponse Successful Response
     * @throws ApiError
     */
    public listCasesApiV1DatasetsDatasetIdCasesGet(
        datasetId: string,
        page: number = 1,
        pageSize: number = 20,
        xOrgId?: (string | null),
    ): CancelablePromise<CaseListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/cases',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Process Variants
     * Get unique activity sequences (variants) with frequencies.
     * @param datasetId
     * @param topN
     * @param topKPercent
     * @param xOrgId
     * @returns VariantResponse Successful Response
     * @throws ApiError
     */
    public getVariantsApiV1DatasetsDatasetIdVariantsGet(
        datasetId: string,
        topN?: (number | null),
        topKPercent?: (number | null),
        xOrgId?: (string | null),
    ): CancelablePromise<Array<VariantResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/variants',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'top_n': topN,
                'top_k_percent': topKPercent,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Activity Statistics
     * Get detailed statistics for each activity.
     * @param datasetId
     * @param sortBy Sort by: frequency, duration
     * @param xOrgId
     * @returns ActivityDetailResponse Successful Response
     * @throws ApiError
     */
    public getActivitiesApiV1DatasetsDatasetIdActivitiesGet(
        datasetId: string,
        sortBy?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<Array<ActivityDetailResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/activities',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'sort_by': sortBy,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Query Events
     * Query events with pagination and filtering.
     *
     * Use this to browse individual events in the event log.
     * @param datasetId
     * @param page
     * @param limit
     * @param caseId Filter by case ID
     * @param activity Filter by activity
     * @param from Start date
     * @param to End date
     * @param xOrgId
     * @returns EventListResponse Successful Response
     * @throws ApiError
     */
    public listEventsApiV1DatasetsDatasetIdEventsGet(
        datasetId: string,
        page: number = 1,
        limit: number = 100,
        caseId?: (string | null),
        activity?: (string | null),
        from?: (string | null),
        to?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<EventListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/events',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'limit': limit,
                'case_id': caseId,
                'activity': activity,
                'from': from,
                'to': to,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Computed Metadata
     * Get computed metadata for a dataset.
     *
     * Includes aggregated statistics computed during ingestion.
     * @param datasetId
     * @param xOrgId
     * @returns MetadataResponse Successful Response
     * @throws ApiError
     */
    public getMetadataApiV1DatasetsDatasetIdMetadataGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<MetadataResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/metadata',
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
}
