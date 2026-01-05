/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectCreateRequest } from '../models/ProjectCreateRequest';
import type { ProjectDetailResponse } from '../models/ProjectDetailResponse';
import type { ProjectListResponse } from '../models/ProjectListResponse';
import type { ProjectResponse } from '../models/ProjectResponse';
import type { ProjectUpdateRequest } from '../models/ProjectUpdateRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ProjectsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Create Project
     * Create a new project, optionally within a workspace.
     *
     * Requires PROJECT_CREATE permission in the workspace.
     * @param requestBody
     * @param workspaceId Workspace ID to associate project with
     * @param xOrgId
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public createProjectApiV1ProjectsPost(
        requestBody: ProjectCreateRequest,
        workspaceId?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/projects',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
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
     * List Projects
     * List all projects with pagination, optionally filtered by workspace.
     *
     * Requires PROJECT_READ permission.
     * Automatically filtered by workspace membership (RLS).
     * @param page
     * @param pageSize
     * @param search Search by project name
     * @param workspaceId Filter by workspace ID
     * @param xOrgId
     * @returns ProjectListResponse Successful Response
     * @throws ApiError
     */
    public listProjectsApiV1ProjectsGet(
        page: number = 1,
        pageSize: number = 20,
        search?: (string | null),
        workspaceId?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/projects',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'search': search,
                'workspace_id': workspaceId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Project
     * Get a project by ID with its datasets.
     *
     * Requires PROJECT_READ permission in the workspace.
     * @param projectId
     * @param xOrgId
     * @returns ProjectDetailResponse Successful Response
     * @throws ApiError
     */
    public getProjectApiV1ProjectsProjectIdGet(
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectDetailResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/projects/{project_id}',
            path: {
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
     * Update Project
     * Update a project.
     *
     * Requires PROJECT_UPDATE permission in the workspace.
     * @param projectId
     * @param requestBody
     * @param xOrgId
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public updateProjectApiV1ProjectsProjectIdPut(
        projectId: string,
        requestBody: ProjectUpdateRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectResponse> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/v1/projects/{project_id}',
            path: {
                'project_id': projectId,
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
     * Delete Project
     * Delete a project.
     *
     * Note: Event logs in this project will have their project_id set to NULL
     * (they won't be deleted).
     *
     * Requires PROJECT_DELETE permission in the workspace.
     * @param projectId
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public deleteProjectApiV1ProjectsProjectIdDelete(
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/projects/{project_id}',
            path: {
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
     * Add File To Project
     * Add an existing dataset to a project.
     *
     * Requires PROJECT_UPDATE permission in the workspace.
     * @param projectId
     * @param datasetId
     * @param xOrgId
     * @returns ProjectDetailResponse Successful Response
     * @throws ApiError
     */
    public addFileToProjectApiV1ProjectsProjectIdFilesDatasetIdPost(
        projectId: string,
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectDetailResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/projects/{project_id}/files/{dataset_id}',
            path: {
                'project_id': projectId,
                'dataset_id': datasetId,
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
     * Remove File From Project
     * Remove a dataset from a project (doesn't delete the dataset).
     *
     * Requires PROJECT_UPDATE permission in the workspace.
     * @param projectId
     * @param datasetId
     * @param xOrgId
     * @returns void
     * @throws ApiError
     */
    public removeFileFromProjectApiV1ProjectsProjectIdFilesDatasetIdDelete(
        projectId: string,
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/projects/{project_id}/files/{dataset_id}',
            path: {
                'project_id': projectId,
                'dataset_id': datasetId,
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
