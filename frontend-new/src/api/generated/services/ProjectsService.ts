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
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ProjectsService {
    /**
     * Create Project
     * Create a new project within a workspace.
     *
     * Projects are containers for organizing event logs (datasets) and their
     * process mining analyses. All projects must belong to a workspace.
     *
     * Requires PROJECT_CREATE permission in the workspace.
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public static createProjectApiV1ProjectsPost({
        workspaceId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Workspace ID to associate project with (required)
         */
        workspaceId: string,
        requestBody: ProjectCreateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectResponse> {
        return __request(OpenAPI, {
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
     * @returns ProjectListResponse Successful Response
     * @throws ApiError
     */
    public static listProjectsApiV1ProjectsGet({
        page = 1,
        pageSize = 20,
        search,
        workspaceId,
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
         * Search by project name
         */
        search?: (string | null),
        /**
         * Filter by workspace ID
         */
        workspaceId?: (string | null),
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectListResponse> {
        return __request(OpenAPI, {
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
     * @returns ProjectDetailResponse Successful Response
     * @throws ApiError
     */
    public static getProjectApiV1ProjectsProjectIdGet({
        projectId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectDetailResponse> {
        return __request(OpenAPI, {
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
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public static updateProjectApiV1ProjectsProjectIdPut({
        projectId,
        requestBody,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        requestBody: ProjectUpdateRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectResponse> {
        return __request(OpenAPI, {
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
     * @returns void
     * @throws ApiError
     */
    public static deleteProjectApiV1ProjectsProjectIdDelete({
        projectId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
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
     * @returns ProjectDetailResponse Successful Response
     * @throws ApiError
     */
    public static addFileToProjectApiV1ProjectsProjectIdFilesDatasetIdPost({
        projectId,
        datasetId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        /**
         * Dataset ID (UUID format)
         */
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectDetailResponse> {
        return __request(OpenAPI, {
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
     * @returns void
     * @throws ApiError
     */
    public static removeFileFromProjectApiV1ProjectsProjectIdFilesDatasetIdDelete({
        projectId,
        datasetId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        /**
         * Dataset ID (UUID format)
         */
        datasetId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<void> {
        return __request(OpenAPI, {
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
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public static archiveProjectApiV1ProjectsProjectIdArchivePost({
        projectId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectResponse> {
        return __request(OpenAPI, {
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
     * @returns ProjectResponse Successful Response
     * @throws ApiError
     */
    public static restoreProjectApiV1ProjectsProjectIdRestorePost({
        projectId,
        xOrgId,
    }: {
        /**
         * Project ID (UUID format)
         */
        projectId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<ProjectResponse> {
        return __request(OpenAPI, {
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
