/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { RunResponse } from './RunResponse';
/**
 * Paginated list of runs.
 */
export type RunListResponse = {
    items: Array<RunResponse>;
    total: number;
    page: number;
    page_size: number;
};

