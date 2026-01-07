/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DevLogsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Stream Logs
     * Stream backend observability to frontend DevConsole via SSE.
     *
     * Returns:
     * - `data:` events for log entries
     * - `event: heartbeat` for system metrics every 5s
     *
     * BUG-034 FIX: Pass user_id to filter logs by tenant.
     * Connect with: `new EventSource('/api/v1/dev/datasets/stream?user_id=xxx')`
     * @param includeRecent Include recent logs on connect
     * @param userId Optional user ID for tenant filtering (BUG-034)
     * @returns any Successful Response
     * @throws ApiError
     */
    public streamLogsApiV1DevLogsStreamGet(
        includeRecent: boolean = true,
        userId?: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/dev/logs/stream',
            query: {
                'include_recent': includeRecent,
                'user_id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current Metrics
     * Get current system metrics snapshot.
     * @returns any Successful Response
     * @throws ApiError
     */
    public getCurrentMetricsApiV1DevLogsMetricsGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/dev/logs/metrics',
        });
    }
    /**
     * Get Recent Logs
     * Get recent logs with optional filtering.
     * @param limit
     * @param level Filter by level
     * @param tag Filter by tag
     * @returns any Successful Response
     * @throws ApiError
     */
    public getRecentLogsApiV1DevLogsRecentGet(
        limit: number = 50,
        level?: (string | null),
        tag?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/dev/logs/recent',
            query: {
                'limit': limit,
                'level': level,
                'tag': tag,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Clear Logs
     * Clear the log buffer and reset metrics.
     * @returns any Successful Response
     * @throws ApiError
     */
    public clearLogsApiV1DevLogsClearDelete(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/dev/logs/clear',
        });
    }
}
