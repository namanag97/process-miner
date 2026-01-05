/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Process variant response with both trace string and parsed activities array.
 */
export type VariantResponse = {
    variant_key: string;
    activity_trace: string;
    activities: Array<string>;
    case_count: number;
    frequency_percent: number;
    avg_duration_seconds?: (number | null);
    complexity_score?: (number | null);
    rework_count?: (number | null);
    unique_activity_count?: (number | null);
};

