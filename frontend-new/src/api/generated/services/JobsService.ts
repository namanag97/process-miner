/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JobCancelResponse } from '../models/JobCancelResponse';
import type { JobListResponse } from '../models/JobListResponse';
import type { JobLogsResponse } from '../models/JobLogsResponse';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class JobsService {
    /**
     * List Jobs
     * List asynchronous jobs with filtering and pagination.
     *
     * Returns paginated list of jobs, ordered by creation time (newest first).
     * @returns JobListResponse Successful Response
     * @throws ApiError
     */
    public static listJobsApiV1JobsGet({
        page = 1,
        pageSize = 20,
        jobType,
        status,
        entityId,
        userId,
    }: {
        /**
         * Page number (1-indexed)
         */
        page?: number,
        /**
         * Items per page (max 100)
         */
        pageSize?: number,
        /**
         * Filter by job type (e.g., ingestion, discovery)
         */
        jobType?: (string | null),
        /**
         * Filter by status (e.g., pending, running, completed, failed)
         */
        status?: (string | null),
        /**
         * Filter by entity ID
         */
        entityId?: (string | null),
        /**
         * Filter by user ID
         */
        userId?: (string | null),
    }): CancelablePromise<JobListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/jobs',
            query: {
                'page': page,
                'page_size': pageSize,
                'job_type': jobType,
                'status': status,
                'entity_id': entityId,
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Status
     * Get the current status and progress of an asynchronous job.
     *
     * Use this endpoint to poll job status for process mining operations
     * like data ingestion, process discovery, or conformance checking.
     * @returns JobStatusResponse Successful Response
     * @throws ApiError
     */
    public static getJobStatusApiV1JobsJobIdGet({
        jobId,
    }: {
        /**
         * Job ID (UUID format)
         */
        jobId: string,
    }): CancelablePromise<JobStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/jobs/{job_id}',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Job
     * Cancel or delete an asynchronous job.
     *
     * - PENDING/QUEUED jobs: Cancelled before execution
     * - RUNNING jobs: Cancellation requested (may take time)
     * - COMPLETED/FAILED/CANCELLED jobs: Deleted from history
     *
     * Returns the final status of the job operation.
     * @returns JobCancelResponse Successful Response
     * @throws ApiError
     */
    public static cancelJobApiV1JobsJobIdDelete({
        jobId,
    }: {
        /**
         * Job ID (UUID format)
         */
        jobId: string,
    }): CancelablePromise<JobCancelResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/jobs/{job_id}',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Stream Job Progress
     * SSE stream for real-time job progress updates.
     *
     * Returns Server-Sent Events as job progresses:
     * - event: job:progress - Progress updates with stage info
     * - event: job:completed - Job completed successfully
     * - event: job:failed - Job failed with error
     *
     * Client should keep connection open and parse SSE events.
     * Connection closes when job completes/fails or client disconnects.
     *
     * Useful for tracking long-running process mining operations like
     * data ingestion, process discovery, or conformance checking.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static streamJobProgressApiV1JobsJobIdStreamGet({
        jobId,
    }: {
        /**
         * Job ID (UUID format)
         */
        jobId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/jobs/{job_id}/stream',
            path: {
                'job_id': jobId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Job Logs
     * Get execution logs for a job.
     *
     * Returns structured log entries for the job's execution.
     * Useful for debugging failed jobs or understanding execution flow.
     * @returns JobLogsResponse Successful Response
     * @throws ApiError
     */
    public static getJobLogsApiV1JobsJobIdLogsGet({
        jobId,
        limit = 100,
        level,
    }: {
        /**
         * Job ID (UUID format)
         */
        jobId: string,
        /**
         * Max log entries to return
         */
        limit?: number,
        /**
         * Filter by log level (info, warn, error)
         */
        level?: (string | null),
    }): CancelablePromise<JobLogsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/jobs/{job_id}/logs',
            path: {
                'job_id': jobId,
            },
            query: {
                'limit': limit,
                'level': level,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
