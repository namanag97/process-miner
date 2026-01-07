/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Available filter options based on log contents.
 */
export type FilterOptionsResponse = {
    activities: Array<string>;
    resources: Array<string>;
    start_activities: Record<string, number>;
    end_activities: Record<string, number>;
    total_variants: number;
    time_range: Record<string, (string | null)>;
    case_size_range: Record<string, number>;
};

