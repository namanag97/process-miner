/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Single rework pattern result.
 */
export type ReworkResponse = {
    activity: string;
    /**
     * Total repeat occurrences
     */
    rework_count: number;
    /**
     * Number of cases with this rework
     */
    cases_with_rework: number;
    /**
     * Percentage of cases with this rework
     */
    rework_percentage: number;
};

