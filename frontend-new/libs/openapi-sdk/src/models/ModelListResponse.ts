/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModelResponse } from './ModelResponse';
/**
 * Paginated model list.
 */
export type ModelListResponse = {
    total: number;
    page: number;
    page_size: number;
    pages: number;
    items: Array<ModelResponse>;
};

