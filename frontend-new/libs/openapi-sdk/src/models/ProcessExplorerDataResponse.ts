/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ActivityDetailResponse } from './ActivityDetailResponse';
import type { DFGResponse } from './DFGResponse';
import type { StatisticsResponse } from './StatisticsResponse';
import type { VariantResponse } from './VariantResponse';
/**
 * Unified response for Process Explorer frontend component.
 *
 * Combines DFG, variants, activities, and statistics in a single request.
 */
export type ProcessExplorerDataResponse = {
    log_id: string;
    dfg: DFGResponse;
    variants: Array<VariantResponse>;
    activities: Array<ActivityDetailResponse>;
    statistics: StatisticsResponse;
};

