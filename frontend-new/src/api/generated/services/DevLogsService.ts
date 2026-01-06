/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DevLogsService {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static streamLogsApiV1DevLogsStreamGet({
        includeRecent = true,
        userId,
    }: {
        /**
         * Include recent logs on connect
         */
        includeRecent?: boolean,
        /**
         * Optional user ID for tenant filtering (BUG-034)
         */
        userId?: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
    public static getCurrentMetricsApiV1DevLogsMetricsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dev/logs/metrics',
        });
    }
    /**
     * Get Recent Logs
     * Get recent logs with optional filtering.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRecentLogsApiV1DevLogsRecentGet({
        limit = 50,
        level,
        tag,
    }: {
        limit?: number,
        /**
         * Filter by level
         */
        level?: (string | null),
        /**
         * Filter by tag
         */
        tag?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
    public static clearLogsApiV1DevLogsClearDelete(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/dev/logs/clear',
        });
    }
}
