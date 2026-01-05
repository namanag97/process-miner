/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AdminUserListResponse } from '../models/AdminUserListResponse';
import type { AdminUserResponse } from '../models/AdminUserResponse';
import type { AdminUserUpdateRequest } from '../models/AdminUserUpdateRequest';
import type { ErrorLogListResponse } from '../models/ErrorLogListResponse';
import type { ErrorLogResponse } from '../models/ErrorLogResponse';
import type { SystemStatsResponse } from '../models/SystemStatsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AdminService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List All Users
     * List all users (superuser only).
     * @param page
     * @param pageSize
     * @param search
     * @param orgId
     * @param xOrgId
     * @returns AdminUserListResponse Successful Response
     * @throws ApiError
     */
    public listAllUsersApiV1AdminUsersGet(
        page: number = 1,
        pageSize: number = 20,
        search?: (string | null),
        orgId?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<AdminUserListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/admin/users',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'search': search,
                'org_id': orgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get User Details
     * Get user details (superuser only).
     * @param userId User ID
     * @param xOrgId
     * @returns AdminUserResponse Successful Response
     * @throws ApiError
     */
    public getUserDetailsApiV1AdminUsersUserIdGet(
        userId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<AdminUserResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/admin/users/{user_id}',
            path: {
                'user_id': userId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update User
     * Update user (superuser only).
     * @param userId User ID
     * @param requestBody
     * @param xOrgId
     * @returns AdminUserResponse Successful Response
     * @throws ApiError
     */
    public updateUserApiV1AdminUsersUserIdPut(
        userId: string,
        requestBody: AdminUserUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<AdminUserResponse> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/v1/admin/users/{user_id}',
            path: {
                'user_id': userId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Disable User
     * Disable user account (superuser only).
     * @param userId User ID
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public disableUserApiV1AdminUsersUserIdDisablePost(
        userId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/admin/users/{user_id}/disable',
            path: {
                'user_id': userId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Errors
     * List error logs (superuser only).
     * @param page
     * @param pageSize
     * @param resolved
     * @param xOrgId
     * @returns ErrorLogListResponse Successful Response
     * @throws ApiError
     */
    public listErrorsApiV1AdminErrorsGet(
        page: number = 1,
        pageSize: number = 20,
        resolved?: (boolean | null),
        xOrgId?: (string | null),
    ): CancelablePromise<ErrorLogListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/admin/errors',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'resolved': resolved,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Error Details
     * Get error details (superuser only).
     * @param errorId Error ID
     * @param xOrgId
     * @returns ErrorLogResponse Successful Response
     * @throws ApiError
     */
    public getErrorDetailsApiV1AdminErrorsErrorIdGet(
        errorId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ErrorLogResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/admin/errors/{error_id}',
            path: {
                'error_id': errorId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Resolve Error
     * Mark error as resolved (superuser only).
     * @param errorId Error ID
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public resolveErrorApiV1AdminErrorsErrorIdResolvePut(
        errorId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/v1/admin/errors/{error_id}/resolve',
            path: {
                'error_id': errorId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get System Stats
     * Get system-wide statistics (superuser only).
     * @param xOrgId
     * @returns SystemStatsResponse Successful Response
     * @throws ApiError
     */
    public getSystemStatsApiV1AdminStatsGet(
        xOrgId?: (string | null),
    ): CancelablePromise<SystemStatsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/admin/stats',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
