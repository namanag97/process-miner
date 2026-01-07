/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Process statistics response.
 */
export type StatisticsResponse = {
    total_events: number;
    total_cases: number;
    total_activities: number;
    total_variants: number;
    activities: Array<string>;
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
    avg_case_duration_seconds: (number | null);
    min_case_duration_seconds: (number | null);
    max_case_duration_seconds: (number | null);
    date_range: (Record<string, string> | null);
};

