/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { src__platform__workflows__schemas__WorkflowResponse } from './src__platform__workflows__schemas__WorkflowResponse';
/**
 * Paginated workflow list.
 */
export type WorkflowListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<src__platform__workflows__schemas__WorkflowResponse>;
};

