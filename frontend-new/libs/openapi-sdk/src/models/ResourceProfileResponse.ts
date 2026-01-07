/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Resource profile details.
 */
export type ResourceProfileResponse = {
    resource: string;
    total_events: number;
    activities: Record<string, number>;
    avg_processing_time_seconds: number;
    first_activity: (string | null);
    last_activity: (string | null);
};

