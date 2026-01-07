/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JobCancelResponse } from '../models/JobCancelResponse';
import type { JobListResponse } from '../models/JobListResponse';
import type { JobLogsResponse } from '../models/JobLogsResponse';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class JobsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Jobs
     * List asynchronous jobs with filtering and pagination.
     *
     * Returns paginated list of jobs, ordered by creation time (newest first).
     * @param page Page number (1-indexed)
     * @param pageSize Items per page (max 100)
     * @param jobType Filter by job type (e.g., ingestion, discovery)
     * @param status Filter by status (e.g., pending, running, completed, failed)
     * @param entityId Filter by entity ID
     * @param userId Filter by user ID
     * @returns JobListResponse Successful Response
     * @throws ApiError
     */
    public listJobsApiV1JobsGet(
        page: number = 1,
        pageSize: number = 20,
        jobType?: (string | null),
        status?: (string | null),
        entityId?: (string | null),
        userId?: (string | null),
    ): CancelablePromise<JobListResponse> {
        return this.httpRequest.request({
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
     * @param jobId Job ID (UUID format)
     * @returns JobStatusResponse Successful Response
     * @throws ApiError
     */
    public getJobStatusApiV1JobsJobIdGet(
        jobId: string,
    ): CancelablePromise<JobStatusResponse> {
        return this.httpRequest.request({
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
     * @param jobId Job ID (UUID format)
     * @returns JobCancelResponse Successful Response
     * @throws ApiError
     */
    public cancelJobApiV1JobsJobIdDelete(
        jobId: string,
    ): CancelablePromise<JobCancelResponse> {
        return this.httpRequest.request({
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
     * @param jobId Job ID (UUID format)
     * @returns any Successful Response
     * @throws ApiError
     */
    public streamJobProgressApiV1JobsJobIdStreamGet(
        jobId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
     * @param jobId Job ID (UUID format)
     * @param limit Max log entries to return
     * @param level Filter by log level (info, warn, error)
     * @returns JobLogsResponse Successful Response
     * @throws ApiError
     */
    public getJobLogsApiV1JobsJobIdLogsGet(
        jobId: string,
        limit: number = 100,
        level?: (string | null),
    ): CancelablePromise<JobLogsResponse> {
        return this.httpRequest.request({
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
