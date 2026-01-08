/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { src__infra__organizations__schemas__OrganizationResponse } from './src__infra__organizations__schemas__OrganizationResponse';
/**
 * Paginated organization list.
 */
export type OrganizationListResponse = {
    items: Array<src__infra__organizations__schemas__OrganizationResponse>;
    total: number;
    page: number;
    page_size: number;
};

