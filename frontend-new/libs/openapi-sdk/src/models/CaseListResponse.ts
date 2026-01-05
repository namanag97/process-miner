/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CaseResponse } from './CaseResponse';
/**
 * Paginated case list.
 */
export type CaseListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<CaseResponse>;
};

