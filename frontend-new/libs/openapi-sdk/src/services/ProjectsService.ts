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
     * Create a new project within a workspace.
     *
     * Projects are containers for organizing event logs (datasets) and their
     * process mining analyses. All projects must belong to a workspace.
     *
     * Requires PROJECT_CREATE permission in the workspace.
     * @param workspaceId Workspace ID to associate project with (required)
     * @param requestBody
     * @param xOrgId
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public createProjectApiV1ProjectsPost(
        workspaceId: string,
        requestBody: ProjectCreateRequest,
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
     * List projects accessible to the current user.
     *
     * Projects are automatically filtered by workspace membership (row-level security).
     * Optionally filter by workspace or search by project name.
     *
     * Requires PROJECT_READ permission.
     * @param page Page number (1-indexed)
     * @param pageSize Items per page (max 100)
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
     * Get a project by ID with its datasets (event logs).
     *
     * Returns project details including all associated datasets for process mining.
     * Requires PROJECT_READ permission in the workspace.
     * @param projectId Project ID (UUID format)
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
     * Update a project's name, description, or tags.
     *
     * Requires PROJECT_UPDATE permission in the workspace.
     * @param projectId Project ID (UUID format)
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
     * Datasets (event logs) in this project are unlinked but not deleted.
     * They can be re-associated with another project.
     *
     * Requires PROJECT_DELETE permission in the workspace.
     * @param projectId Project ID (UUID format)
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
     * Add an existing dataset (event log) to a project.
     *
     * Moves the dataset into this project for organization.
     * Requires PROJECT_UPDATE permission on the project
     * and DATASET_UPDATE permission on the dataset.
     * @param projectId Project ID (UUID format)
     * @param datasetId Dataset ID (UUID format)
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
     * Remove a dataset (event log) from a project.
     *
     * The dataset is unlinked but not deleted - it can be re-associated
     * with another project later.
     *
     * Requires PROJECT_UPDATE permission in the workspace.
     * @param projectId Project ID (UUID format)
     * @param datasetId Dataset ID (UUID format)
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
    /**
     * Archive Project
     * Archive a project.
     *
     * Archived projects are hidden from default list views but still accessible.
     * Requires PROJECT_UPDATE permission (editor+).
     * @param projectId Project ID (UUID format)
     * @param xOrgId
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public archiveProjectApiV1ProjectsProjectIdArchivePost(
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/projects/{project_id}/archive',
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
     * Restore Project
     * Restore an archived project.
     *
     * Restores a previously archived project back to active status.
     * Requires PROJECT_UPDATE permission (editor+).
     * @param projectId Project ID (UUID format)
     * @param xOrgId
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public restoreProjectApiV1ProjectsProjectIdRestorePost(
        projectId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<ProjectResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/projects/{project_id}/restore',
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
}
