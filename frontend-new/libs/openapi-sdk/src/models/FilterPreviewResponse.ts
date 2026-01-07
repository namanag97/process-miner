/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FilterConfig } from './FilterConfig';
import type { FilterStatistics } from './FilterStatistics';
/**
 * Response for filter preview.
 */
export type FilterPreviewResponse = {
    would_retain_cases: number;
    would_retain_events: number;
    statistics: FilterStatistics;
    filters_applied: Array<FilterConfig>;
};

