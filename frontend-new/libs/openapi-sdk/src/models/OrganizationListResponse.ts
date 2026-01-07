/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { OrganizationResponse } from './OrganizationResponse';
/**
 * Paginated organization list.
 */
export type OrganizationListResponse = {
    items: Array<OrganizationResponse>;
    total: number;
    page: number;
    page_size: number;
};

