/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BrowserLog } from '../models/BrowserLog';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TelemetryService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Proxy Traces
     * Proxy OpenTelemetry traces from frontend to DevConsole.
     *
     * Accepts OTLP/HTTP JSON format from browser OpenTelemetry SDK.
     * In dev mode, sends to DevConsole for real-time visualization.
     * In production, would forward to Tempo/Jaeger.
     * @returns any Successful Response
     * @throws ApiError
     */
    public proxyTracesApiV1TelemetryTracesPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/telemetry/traces',
        });
    }
    /**
     * Proxy Logs
     * Proxy browser logs to backend logging infrastructure.
     *
     * In dev mode, sends to DevConsole.
     * In production, would send to Loki.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public proxyLogsApiV1TelemetryLogsPost(
        requestBody: BrowserLog,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/telemetry/logs',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
