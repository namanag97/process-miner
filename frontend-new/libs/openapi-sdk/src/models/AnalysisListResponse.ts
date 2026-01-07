/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AnalysisResponse } from './AnalysisResponse';
/**
 * Paginated analysis list.
 */
export type AnalysisListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<AnalysisResponse>;
};

