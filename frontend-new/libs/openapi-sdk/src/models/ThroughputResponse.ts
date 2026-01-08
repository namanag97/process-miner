/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Throughput metrics.
 */
export type ThroughputResponse = {
    dataset_id: string;
    total_cases: number;
    completed_cases?: number;
    cases_per_day?: number;
    cases_per_week?: number;
    cases_per_month?: number;
    time_range_days?: number;
};

