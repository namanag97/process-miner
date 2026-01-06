/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DatasetResponse } from './DatasetResponse';
/**
 * Paginated dataset list.
 */
export type DatasetListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<DatasetResponse>;
};

