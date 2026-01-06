/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DetailedHealthResponse } from '../models/DetailedHealthResponse';
import type { HealthStatus } from '../models/HealthStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HealthService {
    /**
     * Root
     * Root endpoint with API info.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static rootGet(): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }
    /**
     * Liveness Probe
     * Kubernetes liveness probe.
     *
     * Returns 200 if the process is alive and responding.
     * Used by Kubernetes to restart unhealthy pods.
     * @returns HealthStatus Successful Response
     * @throws ApiError
     */
    public static livenessProbeHealthLiveGet(): CancelablePromise<HealthStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health/live',
        });
    }
    /**
     * Readiness Probe
     * Kubernetes readiness probe.
     *
     * Returns 200 if the service can handle traffic.
     * Checks critical dependencies (database).
     * @returns HealthStatus Successful Response
     * @throws ApiError
     */
    public static readinessProbeHealthReadyGet(): CancelablePromise<HealthStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health/ready',
        });
    }
    /**
     * Startup Probe
     * Kubernetes startup probe.
     *
     * Returns 200 once the application has completed initialization.
     * Used to prevent premature health checks during slow startups.
     * @returns HealthStatus Successful Response
     * @throws ApiError
     */
    public static startupProbeHealthStartupGet(): CancelablePromise<HealthStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health/startup',
        });
    }
    /**
     * Detailed Health
     * Detailed health status for monitoring dashboards.
     *
     * Returns comprehensive status of all components with timing info.
     * @returns DetailedHealthResponse Successful Response
     * @throws ApiError
     */
    public static detailedHealthHealthDetailedGet(): CancelablePromise<DetailedHealthResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health/detailed',
        });
    }
    /**
     * Health Check
     * Basic health check endpoint.
     *
     * Quick check that the service is responding.
     * Use /health/detailed for component-level status.
     * @returns HealthStatus Successful Response
     * @throws ApiError
     */
    public static healthCheckHealthGet(): CancelablePromise<HealthStatus> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/health',
        });
    }
}
