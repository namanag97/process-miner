/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkspaceCreateRequest } from '../models/WorkspaceCreateRequest';
import type { WorkspaceDetailResponse } from '../models/WorkspaceDetailResponse';
import type { WorkspaceListResponse } from '../models/WorkspaceListResponse';
import type { WorkspaceResponse } from '../models/WorkspaceResponse';
import type { WorkspaceUpdateRequest } from '../models/WorkspaceUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkspacesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Workspaces
     * List all workspaces, optionally filtered by organization.
     * @param page
     * @param pageSize
     * @param orgId Filter by organization ID
     * @returns WorkspaceListResponse Successful Response
     * @throws ApiError
     */
    public listWorkspacesApiV1WorkspacesGet(
        page: number = 1,
        pageSize: number = 20,
        orgId?: (string | null),
    ): CancelablePromise<WorkspaceListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workspaces',
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
     * @param orgId Organization ID for the workspace
     * @param requestBody
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public createWorkspaceApiV1WorkspacesPost(
        orgId: string,
        requestBody: WorkspaceCreateRequest,
    ): CancelablePromise<WorkspaceResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/workspaces',
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
     * @param workspaceId
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public getWorkspaceApiV1WorkspacesWorkspaceIdGet(
        workspaceId: string,
    ): CancelablePromise<WorkspaceDetailResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Workspace
     * Update a workspace.
     * @param workspaceId
     * @param requestBody
     * @returns WorkspaceResponse Successful Response
     * @throws ApiError
     */
    public updateWorkspaceApiV1WorkspacesWorkspaceIdPut(
        workspaceId: string,
        requestBody: WorkspaceUpdateRequest,
    ): CancelablePromise<WorkspaceResponse> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
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
     * BUG-036 FIX: Now deletes projects instead of orphaning them.
     * @param workspaceId
     * @returns void
     * @throws ApiError
     */
    public deleteWorkspaceApiV1WorkspacesWorkspaceIdDelete(
        workspaceId: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/workspaces/{workspace_id}',
            path: {
                'workspace_id': workspaceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Project To Workspace
     * Add an existing project to a workspace.
     * @param workspaceId
     * @param projectId
     * @returns WorkspaceDetailResponse Successful Response
     * @throws ApiError
     */
    public addProjectToWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdPost(
        workspaceId: string,
        projectId: string,
    ): CancelablePromise<WorkspaceDetailResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/workspaces/{workspace_id}/projects/{project_id}',
            path: {
                'workspace_id': workspaceId,
                'project_id': projectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Remove Project From Workspace
     * Remove a project from a workspace (doesn't delete the project).
     * @param workspaceId
     * @param projectId
     * @returns void
     * @throws ApiError
     */
    public removeProjectFromWorkspaceApiV1WorkspacesWorkspaceIdProjectsProjectIdDelete(
        workspaceId: string,
        projectId: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/workspaces/{workspace_id}/projects/{project_id}',
            path: {
                'workspace_id': workspaceId,
                'project_id': projectId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
