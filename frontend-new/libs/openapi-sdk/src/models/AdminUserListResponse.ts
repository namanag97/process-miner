/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdminUserResponse } from './AdminUserResponse';
/**
 * Paginated admin user list.
 */
export type AdminUserListResponse = {
    items: Array<AdminUserResponse>;
    total: number;
    page: number;
    page_size: number;
};

