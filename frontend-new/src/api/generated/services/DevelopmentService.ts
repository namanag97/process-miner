/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LogEntry } from '../models/LogEntry';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DevelopmentService {
    /**
     * Receive Log
     * Receive a log entry from frontend and append to dev-logs/app.log.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static receiveLogApiV1DevLogPost({
        requestBody,
    }: {
        requestBody: LogEntry,
    }): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dev/log',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Logs
     * Get recent log entries (for debugging).
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getLogsApiV1DevLogsGet({
        lines = 100,
    }: {
        lines?: number,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dev/logs',
            query: {
                'lines': lines,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Clear Logs
     * Clear the dev log file.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static clearLogsApiV1DevLogsDelete(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/dev/logs',
        });
    }
}
