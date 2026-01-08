/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Cycle time (case duration) statistics.
 */
export type CycleTimeResponse = {
    dataset_id: string;
    /**
     * Minimum case duration in seconds
     */
    min_seconds: number;
    /**
     * Maximum case duration in seconds
     */
    max_seconds: number;
    /**
     * Mean case duration in seconds
     */
    avg_seconds: number;
    /**
     * Median case duration in seconds
     */
    median_seconds: number;
    /**
     * 25th percentile in seconds
     */
    percentile_25_seconds?: number;
    /**
     * 75th percentile in seconds
     */
    percentile_75_seconds?: number;
    /**
     * 95th percentile in seconds
     */
    percentile_95_seconds?: number;
};

