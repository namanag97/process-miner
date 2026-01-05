/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TestService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Test Trace
     * Test endpoint that creates a trace span.
     * @returns any Successful Response
     * @throws ApiError
     */
    public testTraceApiV1TestTelemetryTraceGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/test-telemetry/trace',
        });
    }
}
