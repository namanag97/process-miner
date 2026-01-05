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
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class OrganizationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Organizations
     * List user's organizations.
     * @param page
     * @param pageSize
     * @param xOrgId
     * @returns OrganizationListResponse Successful Response
     * @throws ApiError
     */
    public listOrganizationsApiV1OrganizationsGet(
        page: number = 1,
        pageSize: number = 20,
        xOrgId?: (string | null),
    ): CancelablePromise<OrganizationListResponse> {
        return this.httpRequest.request({
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
     * @param requestBody
     * @param xOrgId
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public createOrganizationApiV1OrganizationsPost(
        requestBody: OrganizationCreateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<OrganizationResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param xOrgId
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public getOrganizationApiV1OrganizationsOrgIdGet(
        orgId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OrganizationResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param requestBody
     * @param xOrgId
     * @returns OrganizationResponse Successful Response
     * @throws ApiError
     */
    public updateOrganizationApiV1OrganizationsOrgIdPut(
        orgId: string,
        requestBody: OrganizationUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<OrganizationResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public deleteOrganizationApiV1OrganizationsOrgIdDelete(
        orgId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param xOrgId
     * @returns MemberListResponse Successful Response
     * @throws ApiError
     */
    public listMembersApiV1OrganizationsOrgIdMembersGet(
        orgId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<MemberListResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param requestBody
     * @param xOrgId
     * @returns MemberResponse Successful Response
     * @throws ApiError
     */
    public inviteMemberApiV1OrganizationsOrgIdMembersInvitePost(
        orgId: string,
        requestBody: InviteMemberRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<MemberResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param userId User ID to remove
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public removeMemberApiV1OrganizationsOrgIdMembersUserIdDelete(
        orgId: string,
        userId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param userId User ID
     * @param requestBody
     * @param xOrgId
     * @returns MemberResponse Successful Response
     * @throws ApiError
     */
    public updateMemberRoleApiV1OrganizationsOrgIdMembersUserIdRolePut(
        orgId: string,
        userId: string,
        requestBody: UpdateRoleRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<MemberResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param xOrgId
     * @returns BillingResponse Successful Response
     * @throws ApiError
     */
    public getBillingApiV1OrganizationsOrgIdBillingGet(
        orgId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<BillingResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID
     * @param xOrgId
     * @returns UsageResponse Successful Response
     * @throws ApiError
     */
    public getUsageApiV1OrganizationsOrgIdUsageGet(
        orgId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<UsageResponse> {
        return this.httpRequest.request({
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
