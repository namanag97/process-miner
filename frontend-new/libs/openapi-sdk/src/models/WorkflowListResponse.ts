/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowResponse } from './WorkflowResponse';
/**
 * Paginated workflow list.
 */
export type WorkflowListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<WorkflowResponse>;
};

