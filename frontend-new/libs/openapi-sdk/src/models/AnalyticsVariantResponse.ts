/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Single process variant for analytics queries (CQRS read model).
 *
 * Note: This is a simpler schema than datasets.VariantResponse.
 * Use this for analytics/performance endpoints.
 * Use datasets.VariantResponse for data exploration endpoints.
 */
export type AnalyticsVariantResponse = {
    variant_id: number;
    /**
     * Sequence of activities in this variant
     */
    activities: Array<string>;
    /**
     * Number of cases following this variant
     */
    case_count: number;
    /**
     * Percentage of total cases
     */
    percentage: number;
};

