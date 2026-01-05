/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Dataset metadata response.
 */
export type MetadataResponse = {
    dataset_id: string;
    total_events: number;
    total_cases: number;
    total_activities: number;
    total_variants: number;
    first_event_at?: (string | null);
    last_event_at?: (string | null);
    avg_case_duration_seconds?: (number | null);
    activities?: Array<string>;
    date_range?: (Record<string, any> | null);
};

