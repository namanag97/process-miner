/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectResponse } from './ProjectResponse';
/**
 * Paginated project list.
 */
export type ProjectListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<ProjectResponse>;
};

