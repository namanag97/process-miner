/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LogEntry } from '../models/LogEntry';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DevelopmentService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Receive Log
     * Receive a log entry from frontend and append to dev-logs/app.log.
     * @param requestBody
     * @returns string Successful Response
     * @throws ApiError
     */
    public receiveLogApiV1DevLogPost(
        requestBody: LogEntry,
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
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
     * @param lines
     * @returns any Successful Response
     * @throws ApiError
     */
    public getLogsApiV1DevLogsGet(
        lines: number = 100,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
    public clearLogsApiV1DevLogsDelete(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/dev/logs',
        });
    }
}
