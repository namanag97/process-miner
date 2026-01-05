/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReworkResponse } from './ReworkResponse';
/**
 * Rework analysis results.
 */
export type ReworkListResponse = {
    log_id: string;
    rework_activities: Array<ReworkResponse>;
    total_rework_cases: number;
    rework_percentage: number;
};

