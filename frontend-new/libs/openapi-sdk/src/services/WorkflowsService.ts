/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowListResponse } from '../models/WorkflowListResponse';
import type { WorkflowResponse } from '../models/WorkflowResponse';
import type { WorkflowTaskResponse } from '../models/WorkflowTaskResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkflowsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Workflows
     * List workflows for the current user/organization.
     *
     * Use entity_type + entity_id to get workflows for a specific dataset/model.
     * @param status Filter by status
     * @param workflowType Filter by type
     * @param entityType Filter by entity type
     * @param entityId Filter by entity ID
     * @param limit
     * @param offset
     * @param xOrgId
     * @returns WorkflowListResponse Successful Response
     * @throws ApiError
     */
    public listWorkflowsApiV1WorkflowsGet(
        status?: (string | null),
        workflowType?: (string | null),
        entityType?: (string | null),
        entityId?: (string | null),
        limit: number = 20,
        offset?: number,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkflowListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workflows',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'status': status,
                'workflow_type': workflowType,
                'entity_type': entityType,
                'entity_id': entityId,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Workflow
     * Get workflow details with task-level progress.
     * @param workflowId
     * @param xOrgId
     * @returns WorkflowResponse Successful Response
     * @throws ApiError
     */
    public getWorkflowApiV1WorkflowsWorkflowIdGet(
        workflowId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<WorkflowResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workflows/{workflow_id}',
            path: {
                'workflow_id': workflowId,
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
     * Get Workflow Tasks
     * Get granular task progress for a workflow.
     *
     * Returns ordered list of tasks with their individual status and progress.
     * @param workflowId
     * @param xOrgId
     * @returns WorkflowTaskResponse Successful Response
     * @throws ApiError
     */
    public getWorkflowTasksApiV1WorkflowsWorkflowIdTasksGet(
        workflowId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Array<WorkflowTaskResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workflows/{workflow_id}/tasks',
            path: {
                'workflow_id': workflowId,
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
