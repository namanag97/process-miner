/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityDetailResponse } from '../models/ActivityDetailResponse';
import type { Body_detect_columns_api_v1_datasets_detect_columns_post } from '../models/Body_detect_columns_api_v1_datasets_detect_columns_post';
import type { Body_upload_dataset_api_v1_datasets_upload_post } from '../models/Body_upload_dataset_api_v1_datasets_upload_post';
import type { CaseListResponse } from '../models/CaseListResponse';
import type { ColumnDetectionResponse } from '../models/ColumnDetectionResponse';
import type { DataPreviewResponse } from '../models/DataPreviewResponse';
import type { DatasetDetailResponse } from '../models/DatasetDetailResponse';
import type { DatasetListResponse } from '../models/DatasetListResponse';
import type { DatasetResponse } from '../models/DatasetResponse';
import type { IngestRequest } from '../models/IngestRequest';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { PresignedUploadRequest } from '../models/PresignedUploadRequest';
import type { PresignedUploadResponse } from '../models/PresignedUploadResponse';
import type { SheetsResponse } from '../models/SheetsResponse';
import type { StatisticsResponse } from '../models/StatisticsResponse';
import type { VariantResponse } from '../models/VariantResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DatasetsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Presigned S3 Upload URL
     * Generate a short-lived presigned URL for direct S3 upload.
     *
     * ## Use Case
     * *   **Large Files**: Bypass the API server for files > 10MB.
     * *   **Performance**: Faster upload speeds via direct S3 connection.
     *
     * ## Flow
     * 1.  Call this endpoint to get `upload_url`.
     * 2.  PUT the file to `upload_url`.
     * 3.  Call `POST /datasets/{id}/trigger-validation` to start processing.
     * @param requestBody
     * @param xOrgId
     * @returns PresignedUploadResponse Presigned URL generated successfully
     * @throws ApiError
     */
    public getPresignedUploadUrlApiV1DatasetsUploadPresignedPost(
        requestBody: PresignedUploadRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<PresignedUploadResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/upload/presigned',
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
     * Trigger Dataset Validation
     * Start the background validation and ingestion process after a successful S3 upload.
     *
     * ## When to use
     * Call this **only** after successfully uploading a file to the presigned URL obtained from `/upload/presigned`.
     * @param datasetId
     * @param xOrgId
     * @returns string Validation task queued
     * @throws ApiError
     */
    public triggerValidationApiV1DatasetsDatasetIdTriggerValidationPost(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/trigger-validation',
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
     * Upload Event Log File
     * Upload and ingest an event log file (CSV or XES).
     *
     * ## Features
     * *   **Auto-detection**: Smart column detection for CSV files.
     * *   **Streaming**: efficiently handles large files (up to 100MB) without memory issues.
     * *   **Async Store**: Optional deferred processing for very large datasets.
     *
     * ## Form Parameters
     * *   `file`: The file to upload.
     * *   `project_id`: Target project ID.
     * *   `case_id_column` etc.: Manual mapping overrides.
     * @param formData
     * @param xOrgId
     * @returns DatasetResponse Dataset created and ingested successfully
     * @throws ApiError
     */
    public uploadDatasetApiV1DatasetsUploadPost(
        formData: Body_upload_dataset_api_v1_datasets_upload_post,
        xOrgId?: (string | null),
    ): CancelablePromise<DatasetResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/upload',
            headers: {
                'X-Org-Id': xOrgId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                400: `Invalid file format or missing columns`,
                413: `File too large (exceeds 100MB)`,
                422: `Validation error (missing project_id)`,
            },
        });
    }
    /**
     * Detect Columns
     * Detect column mappings from a CSV file.
     *
     * Returns suggested mappings for case_id, activity, timestamp, and resource columns.
     *
     * Requires DATASET_READ permission (public utility endpoint for authenticated users).
     * @param formData
     * @param xOrgId
     * @returns ColumnDetectionResponse Successful Response
     * @throws ApiError
     */
    public detectColumnsApiV1DatasetsDetectColumnsPost(
        formData: Body_detect_columns_api_v1_datasets_detect_columns_post,
        xOrgId?: (string | null),
    ): CancelablePromise<ColumnDetectionResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/detect-columns',
            headers: {
                'X-Org-Id': xOrgId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Ingest Dataset
     * Trigger background ingestion for an AWAITING_MAPPING dataset.
     *
     * Job-Centric Architecture: Returns 202 with job_id for progress tracking.
     *
     * Phase 2 of deferred ingestion: user provides column mapping,
     * background worker parses file and computes variants.
     *
     * Returns AsyncJob status for progress tracking via GET /jobs/{job_id}.
     *
     * Requires DATASET_UPDATE permission in the workspace.
     * @param datasetId
     * @param requestBody
     * @param xOrgId
     * @returns JobStatusResponse Successful Response
     * @throws ApiError
     */
    public ingestDatasetApiV1DatasetsDatasetIdIngestPost(
        datasetId: string,
        requestBody: IngestRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<JobStatusResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/datasets/{dataset_id}/ingest',
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
     * Detect Columns For Dataset
     * Detect column mappings from an already-uploaded UNSTRUCTURED dataset.
     *
     * Reads the stored file and returns suggested mappings for case_id,
     * activity, timestamp, and resource columns.
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param xOrgId
     * @returns ColumnDetectionResponse Successful Response
     * @throws ApiError
     */
    public detectColumnsForDatasetApiV1DatasetsDatasetIdDetectColumnsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ColumnDetectionResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/detect-columns',
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
     * Get Data Preview
     * Get data preview with column types for upload wizard Configure step.
     *
     * Returns:
     * - Column names with detected types (STRING, INTEGER, DATETIME, etc.)
     * - Sample preview rows
     * - Parsing configuration info
     *
     * Supports navigation away and back - data is preserved in storage.
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param rows Number of preview rows
     * @param xOrgId
     * @returns DataPreviewResponse Successful Response
     * @throws ApiError
     */
    public getDataPreviewApiV1DatasetsDatasetIdPreviewGet(
        datasetId: string,
        rows: number = 10,
        xOrgId?: (string | null),
    ): CancelablePromise<DataPreviewResponse> {
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Sheets
     * List available sheets in an Excel file.
     *
     * For CSV files, returns a single pseudo-sheet.
     * Required for upload wizard Step 2 (Select Sheet).
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param xOrgId
     * @returns SheetsResponse Successful Response
     * @throws ApiError
     */
    public getSheetsApiV1DatasetsDatasetIdSheetsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<SheetsResponse> {
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
     * List Datasets
     * List all uploaded datasets.
     *
     * Supports pagination and filtering by source format.
     *
     * Requires DATASET_READ permission.
     * Automatically filtered by workspace membership (RLS).
     * @param page
     * @param pageSize
     * @param sourceFormat
     * @param projectId Filter by project ID
     * @param xOrgId
     * @returns DatasetListResponse Successful Response
     * @throws ApiError
     */
    public listDatasetsApiV1DatasetsGet(
        page: number = 1,
        pageSize: number = 20,
        sourceFormat?: (string | null),
        projectId?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<DatasetListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'source_format': sourceFormat,
                'project_id': projectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Dataset
     * Get detailed information about an event log.
     *
     * Requires DATASET_READ permission in the workspace.
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
     * Delete an event log and all associated data.
     *
     * Requires DATASET_DELETE permission in the workspace.
     *
     * BUG-052 FIX: Also deletes orphaned recommendations.
     * SECURITY: Added authentication and permission check (Phase 6.2)
     * @param datasetId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteDatasetApiV1DatasetsDatasetIdDelete(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
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
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Statistics
     * Get comprehensive statistics for an event log.
     *
     * Includes activities, variants, case durations, and more.
     *
     * PERFORMANCE: Uses SQL aggregations instead of ORM eager loading
     * to prevent OOM on large datasets (1M+ events).
     *
     * Requires DATASET_READ permission in the workspace.
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
     * List cases in an event log with pagination.
     *
     * Requires DATASET_READ permission in the workspace.
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
     * Get Variants
     * Get process variants (unique activity sequences) with frequencies.
     *
     * Supports filtering by:
     * - top_n: Return top N variants by case count
     * - top_k_percent: Return variants covering top K% of cases
     *
     * When include_complexity=true, each variant includes:
     * - complexity_score: 0-1 score based on length, rework, and repetition
     * - rework_count: Number of repeated activities
     * - unique_activity_count: Number of distinct activities
     *
     * PERFORMANCE: Uses SQL aggregation instead of ORM iteration to avoid loading
     * millions of objects into memory.
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param topN
     * @param topKPercent Return variants covering top K% of cases
     * @param includeComplexity Include complexity metrics (score, rework count, unique activities)
     * @param sortBy Sort variants by: 'frequency', 'complexity', 'duration'. Default: frequency
     * @param xOrgId
     * @returns VariantResponse Successful Response
     * @throws ApiError
     */
    public getVariantsApiV1DatasetsDatasetIdVariantsGet(
        datasetId: string,
        topN: number = 20,
        topKPercent?: (number | null),
        includeComplexity: boolean = false,
        sortBy?: (string | null),
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
                'include_complexity': includeComplexity,
                'sort_by': sortBy,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Activities
     * Get detailed activity statistics for a process.
     *
     * Returns each activity with:
     * - frequency: Total occurrences
     * - frequency_percent: Percentage of total events
     * - avg/min/max_duration_seconds: Time to next activity
     * - is_start_activity/is_end_activity: Position flags
     * - position_avg: Average normalized position (0=start, 1=end)
     *
     * PERFORMANCE: Uses event_log_loader (DuckDB/Arrow) instead of ORM iteration
     * to avoid loading millions of objects into memory.
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param sortBy Sort activities by: 'frequency', 'duration', 'position'. Default: frequency
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
     * Get Domain Analysis
     * Get process analysis using the new rich domain model.
     *
     * This endpoint demonstrates the improved architecture:
     * 1. Repository pattern for data access
     * 2. DatasetAggregate for domain logic
     * 3. PM4Py log caching (single conversion)
     * 4. Computed properties on domain entities
     *
     * Returns aggregate statistics, variant analysis, and PM4Py cache status.
     *
     * Requires DATASET_READ permission in the workspace.
     * @param datasetId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDomainAnalysisApiV1DatasetsDatasetIdDomainAnalysisGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/datasets/{dataset_id}/domain/analysis',
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
