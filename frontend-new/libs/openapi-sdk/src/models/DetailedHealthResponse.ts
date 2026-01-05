/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ComponentHealth } from './ComponentHealth';
/**
 * Detailed health response with component breakdown.
 */
export type DetailedHealthResponse = {
    status: string;
    version: string;
    uptime_seconds: number;
    timestamp: string;
    components: Array<ComponentHealth>;
};

