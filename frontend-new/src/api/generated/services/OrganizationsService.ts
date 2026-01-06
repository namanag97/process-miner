/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BillingResponse } from '../models/BillingResponse';
import type { InviteMemberRequest } from '../models/InviteMemberRequest';
import type { MemberListResponse } from '../models/MemberListResponse';
import type { MemberResponse } from '../models/MemberResponse';
import type { OrganizationCreateRequest } from '../models/OrganizationCreateRequest';
import type { OrganizationListResponse } from '../models/OrganizationListResponse';
import type { OrganizationResponse } from '../models/OrganizationResponse';
import type { OrganizationUpdateRequest } from '../models/OrganizationUpdateRequest';
import type { UpdateRoleRequest } from '../models/UpdateRoleRequest';
import type { UsageResponse } from '../models/UsageResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class OrganizationsService {
    /**
     * List Organizations
     * List user's organizations.
     * @returns OrganizationListResponse Successful Response
     * @throws ApiError
     */
    public static listOrganizationsApiV1OrganizationsGet({
        page = 1,
        pageSize = 20,
        xOrgId,
    }: {
        page?: number,
        pageSize?: number,
        xOrgId?: (string | null),
    }): CancelablePromise<OrganizationListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/organizations/',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Organization
     * Create new organization.
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public static createOrganizationApiV1OrganizationsPost({
        requestBody,
        xOrgId,
    }: {
        requestBody: OrganizationCreateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<OrganizationResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/organizations/',
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
     * Get Organization
     * Get organization details.
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public static getOrganizationApiV1OrganizationsOrgIdGet({
        orgId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<OrganizationResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/organizations/{org_id}',
            path: {
                'org_id': orgId,
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
     * Update Organization
     * Update organization (admin only).
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public static updateOrganizationApiV1OrganizationsOrgIdPut({
        orgId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        requestBody: OrganizationUpdateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<OrganizationResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/organizations/{org_id}',
            path: {
                'org_id': orgId,
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
     * Delete Organization
     * Delete organization (owner only).
     * @returns void
     * @throws ApiError
     */
    public static deleteOrganizationApiV1OrganizationsOrgIdDelete({
        orgId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/organizations/{org_id}',
            path: {
                'org_id': orgId,
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
     * List Members
     * List organization members.
     * @returns MemberListResponse Successful Response
     * @throws ApiError
     */
    public static listMembersApiV1OrganizationsOrgIdMembersGet({
        orgId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<MemberListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/organizations/{org_id}/members',
            path: {
                'org_id': orgId,
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
     * Invite Member
     * Invite user to organization (admin only).
     * @returns MemberResponse Successful Response
     * @throws ApiError
     */
    public static inviteMemberApiV1OrganizationsOrgIdMembersInvitePost({
        orgId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        requestBody: InviteMemberRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<MemberResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/organizations/{org_id}/members/invite',
            path: {
                'org_id': orgId,
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
     * Remove Member
     * Remove member from organization (admin only).
     * @returns void
     * @throws ApiError
     */
    public static removeMemberApiV1OrganizationsOrgIdMembersUserIdDelete({
        orgId,
        userId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        /**
         * User ID to remove
         */
        userId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/organizations/{org_id}/members/{user_id}',
            path: {
                'org_id': orgId,
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
     * Update Member Role
     * Change member role (owner only).
     * @returns MemberResponse Successful Response
     * @throws ApiError
     */
    public static updateMemberRoleApiV1OrganizationsOrgIdMembersUserIdRolePut({
        orgId,
        userId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        /**
         * User ID
         */
        userId: string,
        requestBody: UpdateRoleRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<MemberResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/organizations/{org_id}/members/{user_id}/role',
            path: {
                'org_id': orgId,
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
     * Get Billing
     * Get billing info (placeholder - admin only).
     * @returns BillingResponse Successful Response
     * @throws ApiError
     */
    public static getBillingApiV1OrganizationsOrgIdBillingGet({
        orgId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<BillingResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/organizations/{org_id}/billing',
            path: {
                'org_id': orgId,
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
     * Get Usage
     * Get usage stats (admin only).
     * @returns UsageResponse Successful Response
     * @throws ApiError
     */
    public static getUsageApiV1OrganizationsOrgIdUsageGet({
        orgId,
        xOrgId,
    }: {
        /**
         * Organization ID
         */
        orgId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<UsageResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/organizations/{org_id}/usage',
            path: {
                'org_id': orgId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
