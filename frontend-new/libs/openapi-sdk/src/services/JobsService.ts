/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JobListResponse } from '../models/JobListResponse';
import type { JobStatusResponse } from '../models/JobStatusResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class JobsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Jobs
     * List asynchronous jobs with filtering and pagination.
     * @param page
     * @param pageSize
     * @param jobType
     * @param status
     * @param entityId
     * @param userId
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
     * @param jobId
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
     * @param jobId
     * @returns any Successful Response
     * @throws ApiError
     */
    public cancelJobApiV1JobsJobIdDelete(
        jobId: string,
    ): CancelablePromise<any> {
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
     * @param jobId
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
}
