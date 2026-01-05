/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Health status for a single component.
 */
export type ComponentHealth = {
    name: string;
    status: string;
    latency_ms?: (number | null);
    message?: (string | null);
    details?: (Record<string, any> | null);
};

