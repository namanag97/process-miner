/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { FilterConfig } from './FilterConfig';
import type { FilterStatistics } from './FilterStatistics';
/**
 * Response for a filtered log.
 */
export type FilteredLogResponse = {
    id: string;
    name: string;
    source_log_id?: string;
    is_filtered?: boolean;
    filter_config?: Array<FilterConfig>;
    total_events: number;
    total_cases: number;
    total_activities: number;
    statistics?: (FilterStatistics | null);
    created_at: string;
};

