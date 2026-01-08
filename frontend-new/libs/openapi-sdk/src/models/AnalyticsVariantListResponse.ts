/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalyticsVariantResponse } from './AnalyticsVariantResponse';
/**
 * Process variants analysis results from CQRS query.
 */
export type AnalyticsVariantListResponse = {
    dataset_id: string;
    variants: Array<AnalyticsVariantResponse>;
    total_variants: number;
    total_cases: number;
};

