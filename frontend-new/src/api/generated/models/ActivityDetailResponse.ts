/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Detailed activity statistics for process explorer.
 */
export type ActivityDetailResponse = {
    activity: string;
    frequency: number;
    frequency_percent: number;
    avg_duration_seconds?: (number | null);
    min_duration_seconds?: (number | null);
    max_duration_seconds?: (number | null);
    is_start_activity?: boolean;
    is_end_activity?: boolean;
    position_avg?: (number | null);
    resources?: Array<string>;
};

