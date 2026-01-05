/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkspaceResponse } from './WorkspaceResponse';
/**
 * Paginated workspace list.
 */
export type WorkspaceListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<WorkspaceResponse>;
};

