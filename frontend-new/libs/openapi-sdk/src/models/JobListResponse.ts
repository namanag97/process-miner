/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { JobStatusResponse } from './JobStatusResponse';
/**
 * Paginated job list.
 */
export type JobListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<JobStatusResponse>;
};

