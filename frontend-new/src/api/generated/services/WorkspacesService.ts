/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AddMemberRequest } from '../models/AddMemberRequest';
import type { UpdateMemberRoleRequest } from '../models/UpdateMemberRoleRequest';
import type { WorkspaceCreateRequest } from '../models/WorkspaceCreateRequest';
import type { WorkspaceDetailResponse } from '../models/WorkspaceDetailResponse';
import type { WorkspaceListResponse } from '../models/WorkspaceListResponse';
import type { WorkspaceMemberListResponse } from '../models/WorkspaceMemberListResponse';
import type { WorkspaceMemberResponseInline } from '../models/WorkspaceMemberResponseInline';
import type { WorkspaceResponse } from '../models/WorkspaceResponse';
import type { WorkspaceUpdateRequest } from '../models/WorkspaceUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WorkspacesService {
    /**
     * List Workspaces
     * List workspaces accessible to the current user.
     *
     * In multi-tenant SaaS mode, returns only workspaces where user is a member.
     * Optionally filter by organization ID.
     * @returns WorkspaceListResponse Successful Response
     * @throws ApiError
     */
    public static listWorkspacesApiV1WorkspacesGet({
        page = 1,
        pageSize = 20,
        orgId,
        xOrgId,
    }: {
        /**
         * Page number (1-indexed)
         */
        page?: number,
        /**
         * Items per page (max 100)
         */
        pageSize?: number,
        /**
         * Filter by organization ID
         */
        orgId?: (string | null),
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workspaces',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'org_id': orgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Workspace
     * Create a new workspace within an organization.
     *
     * The creating user automatically becomes the workspace owner.
     * Requires user to be a member of the organization.
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public static createWorkspaceApiV1WorkspacesPost({
        orgId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Organization ID for the workspace
         */
        orgId: string,
        requestBody: WorkspaceCreateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workspaces',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'org_id': orgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Workspace
     * Get a workspace by ID with its projects.
     *
     * Requires WORKSPACE_READ permission (membership in the workspace).
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public static getWorkspaceApiV1WorkspacesWorkspaceIdGet({
        workspaceId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceDetailResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
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
     * Update Workspace
     * Update a workspace's name or description.
     *
     * Requires WORKSPACE_UPDATE permission (admin or owner role).
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public static updateWorkspaceApiV1WorkspacesWorkspaceIdPut({
        workspaceId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        requestBody: WorkspaceUpdateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
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
     * Delete Workspace
     * Delete a workspace and all its projects.
     *
     * Requires WORKSPACE_DELETE permission (owner role only).
     * WARNING: This permanently deletes all projects in the workspace.
     * @returns void
     * @throws ApiError
     */
    public static deleteWorkspaceApiV1WorkspacesWorkspaceIdDelete({
        workspaceId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
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
     * Add Project To Workspace
     * Move an existing project into this workspace.
     *
     * Requires WORKSPACE_UPDATE permission on the target workspace
     * and PROJECT_UPDATE permission on the project.
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public static addProjectToWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdPost({
        workspaceId,
        projectId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceDetailResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workspaces/{workspace_id}/projects/{project_id}',
            path: {
                'workspace_id': workspaceId,
                'project_id': projectId,
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
     * Remove Project From Workspace
     * Remove a project from a workspace (doesn't delete the project).
     *
     * The project becomes unassigned and can be re-associated with another workspace.
     * Requires WORKSPACE_UPDATE permission.
     * @returns void
     * @throws ApiError
     */
    public static removeProjectFromWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdDelete({
        workspaceId,
        projectId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/workspaces/{workspace_id}/projects/{project_id}',
            path: {
                'workspace_id': workspaceId,
                'project_id': projectId,
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
     * List Workspace Members
     * List workspace members.
     * @returns WorkspaceMemberListResponse Successful Response
     * @throws ApiError
     */
    public static listWorkspaceMembersApiV1WorkspacesWorkspaceIdMembersGet({
        workspaceId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceMemberListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workspaces/{workspace_id}/members',
            path: {
                'workspace_id': workspaceId,
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
     * Add Workspace Member
     * Add member to workspace (admin only).
     * @returns WorkspaceMemberResponseInline Successful Response
     * @throws ApiError
     */
    public static addWorkspaceMemberApiV1WorkspacesWorkspaceIdMembersPost({
        workspaceId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        requestBody: AddMemberRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceMemberResponseInline> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workspaces/{workspace_id}/members',
            path: {
                'workspace_id': workspaceId,
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
     * Update Workspace Member Role
     * Update member role (admin only).
     * @returns WorkspaceMemberResponseInline Successful Response
     * @throws ApiError
     */
    public static updateWorkspaceMemberRoleApiV1WorkspacesWorkspaceIdMembersUserIdPut({
        workspaceId,
        userId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        /**
         * User ID
         */
        userId: string,
        requestBody: UpdateMemberRoleRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkspaceMemberResponseInline> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/v1/workspaces/{workspace_id}/members/{user_id}',
            path: {
                'workspace_id': workspaceId,
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
     * Remove Workspace Member
     * Remove member from workspace (admin only).
     * @returns void
     * @throws ApiError
     */
    public static removeWorkspaceMemberApiV1WorkspacesWorkspaceIdMembersUserIdDelete({
        workspaceId,
        userId,
        xOrgId,
    }: {
        /**
         * Workspace ID (UUID format)
         */
        workspaceId: string,
        /**
         * User ID
         */
        userId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/workspaces/{workspace_id}/members/{user_id}',
            path: {
                'workspace_id': workspaceId,
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
}
