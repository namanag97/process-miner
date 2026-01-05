/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ConformanceResponse } from './ConformanceResponse';
/**
 * Paginated conformance results list.
 */
export type ConformanceListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<ConformanceResponse>;
};

