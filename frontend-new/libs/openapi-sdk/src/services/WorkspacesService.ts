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
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkspacesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Workspaces
     * List workspaces accessible to the current user.
     *
     * In multi-tenant SaaS mode, returns only workspaces where user is a member.
     * Optionally filter by organization ID.
     * @param page Page number (1-indexed)
     * @param pageSize Items per page (max 100)
     * @param orgId Filter by organization ID
     * @param xOrgId
     * @returns WorkspaceListResponse Successful Response
     * @throws ApiError
     */
    public listWorkspacesApiV1WorkspacesGet(
        page: number = 1,
        pageSize: number = 20,
        orgId?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceListResponse> {
        return this.httpRequest.request({
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
     * @param orgId Organization ID for the workspace
     * @param requestBody
     * @param xOrgId
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public createWorkspaceApiV1WorkspacesPost(
        orgId: string,
        requestBody: WorkspaceCreateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceResponse> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param xOrgId
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public getWorkspaceApiV1WorkspacesWorkspaceIdGet(
        workspaceId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceDetailResponse> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param requestBody
     * @param xOrgId
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public updateWorkspaceApiV1WorkspacesWorkspaceIdPut(
        workspaceId: string,
        requestBody: WorkspaceUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceResponse> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public deleteWorkspaceApiV1WorkspacesWorkspaceIdDelete(
        workspaceId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param projectId Project ID (UUID format)
     * @param xOrgId
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public addProjectToWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdPost(
        workspaceId: string,
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceDetailResponse> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param projectId Project ID (UUID format)
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public removeProjectFromWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdDelete(
        workspaceId: string,
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param xOrgId
     * @returns WorkspaceMemberListResponse Successful Response
     * @throws ApiError
     */
    public listWorkspaceMembersApiV1WorkspacesWorkspaceIdMembersGet(
        workspaceId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceMemberListResponse> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param requestBody
     * @param xOrgId
     * @returns WorkspaceMemberResponseInline Successful Response
     * @throws ApiError
     */
    public addWorkspaceMemberApiV1WorkspacesWorkspaceIdMembersPost(
        workspaceId: string,
        requestBody: AddMemberRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceMemberResponseInline> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param userId User ID
     * @param requestBody
     * @param xOrgId
     * @returns WorkspaceMemberResponseInline Successful Response
     * @throws ApiError
     */
    public updateWorkspaceMemberRoleApiV1WorkspacesWorkspaceIdMembersUserIdPut(
        workspaceId: string,
        userId: string,
        requestBody: UpdateMemberRoleRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkspaceMemberResponseInline> {
        return this.httpRequest.request({
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
     * @param workspaceId Workspace ID (UUID format)
     * @param userId User ID
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public removeWorkspaceMemberApiV1WorkspacesWorkspaceIdMembersUserIdDelete(
        workspaceId: string,
        userId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
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
