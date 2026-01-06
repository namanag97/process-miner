/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Step configuration for DAG definition.
 */
export type StepConfig = {
    /**
     * Unique step name within the DAG
     */
    name: string;
    /**
     * Registered task function name
     */
    task_name: string;
    /**
     * Default parameters for the task
     */
    default_params?: Record<string, any>;
    /**
     * Retry configuration (max_retries, backoff)
     */
    retry_policy?: (Record<string, any> | null);
    /**
     * Task timeout in seconds
     */
    timeout_seconds?: number;
};

