/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ErrorLogResponse } from './ErrorLogResponse';
/**
 * Paginated error log list.
 */
export type ErrorLogListResponse = {
    items: Array<ErrorLogResponse>;
    total: number;
    page: number;
    page_size: number;
};

