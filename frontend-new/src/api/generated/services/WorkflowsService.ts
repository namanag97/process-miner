/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { src__platform__workflows__schemas__WorkflowResponse } from '../models/src__platform__workflows__schemas__WorkflowResponse';
import type { WorkflowCreateRequest } from '../models/WorkflowCreateRequest';
import type { WorkflowListResponse } from '../models/WorkflowListResponse';
import type { WorkflowResponse } from '../models/WorkflowResponse';
import type { WorkflowRunRequest } from '../models/WorkflowRunRequest';
import type { WorkflowRunResponse } from '../models/WorkflowRunResponse';
import type { WorkflowTaskResponse } from '../models/WorkflowTaskResponse';
import type { WorkflowTemplate } from '../models/WorkflowTemplate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class WorkflowsService {
    /**
     * List Templates
     * List predefined workflow templates.
     *
     * Note: Consider using DAG templates via GET /api/v1/dags/templates instead.
     * @returns WorkflowTemplate Successful Response
     * @throws ApiError
     */
    public static listTemplatesApiV1WorkflowsTemplatesGet(): CancelablePromise<Array<WorkflowTemplate>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workflows/templates',
        });
    }
    /**
     * List Workflows
     * List workflows for the current user/organization.
     *
     * Use entity_type + entity_id to get workflows for a specific dataset/model.
     * @returns WorkflowListResponse Successful Response
     * @throws ApiError
     */
    public static listWorkflowsApiV1WorkflowsGet({
        status,
        workflowType,
        entityType,
        entityId,
        limit = 20,
        offset,
        xOrgId,
    }: {
        /**
         * Filter by status
         */
        status?: (string | null),
        /**
         * Filter by type
         */
        workflowType?: (string | null),
        /**
         * Filter by entity type
         */
        entityType?: (string | null),
        /**
         * Filter by entity ID
         */
        entityId?: (string | null),
        limit?: number,
        offset?: number,
        xOrgId?: (string | null),
    }): CancelablePromise<WorkflowListResponse> {
        return __request(OpenAPI, {
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
     * Create Workflow
     * Create a new workflow.
     *
     * Note: Consider using POST /api/v1/dags instead for new workflows.
     * @returns WorkflowResponse Successful Response
     * @throws ApiError
     */
    public static createWorkflowApiV1WorkflowsPost({
        requestBody,
    }: {
        requestBody: WorkflowCreateRequest,
    }): CancelablePromise<WorkflowResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workflows',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Workflow
     * Get workflow details with task-level progress.
     * @returns src__platform__workflows__schemas__WorkflowResponse Successful Response
     * @throws ApiError
     */
    public static getWorkflowApiV1WorkflowsWorkflowIdGet({
        workflowId,
        xOrgId,
    }: {
        workflowId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<src__platform__workflows__schemas__WorkflowResponse> {
        return __request(OpenAPI, {
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
     * Delete Workflow
     * Delete a workflow.
     *
     * Note: Use DELETE /api/v1/dags/{id} instead.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteWorkflowApiV1WorkflowsWorkflowIdDelete({
        workflowId,
    }: {
        workflowId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/workflows/{workflow_id}',
            path: {
                'workflow_id': workflowId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Run Workflow
     * Execute a workflow.
     *
     * Note: Use POST /api/v1/dags/{id}/trigger instead.
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public static runWorkflowApiV1WorkflowsWorkflowIdRunPost({
        workflowId,
        requestBody,
    }: {
        workflowId: string,
        requestBody: WorkflowRunRequest,
    }): CancelablePromise<WorkflowRunResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workflows/{workflow_id}/run',
            path: {
                'workflow_id': workflowId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Workflow Runs
     * List runs for a workflow.
     *
     * Note: Use GET /api/v1/dags/runs instead.
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public static listWorkflowRunsApiV1WorkflowsWorkflowIdRunsGet({
        workflowId,
    }: {
        workflowId: string,
    }): CancelablePromise<Array<WorkflowRunResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workflows/{workflow_id}/runs',
            path: {
                'workflow_id': workflowId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Workflow Run
     * Get a specific workflow run.
     *
     * Note: Use GET /api/v1/dags/runs/{id} instead.
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public static getWorkflowRunApiV1WorkflowsRunsRunIdGet({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<WorkflowRunResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workflows/runs/{run_id}',
            path: {
                'run_id': runId,
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
     * @returns WorkflowTaskResponse Successful Response
     * @throws ApiError
     */
    public static getWorkflowTasksApiV1WorkflowsWorkflowIdTasksGet({
        workflowId,
        xOrgId,
    }: {
        workflowId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<Array<WorkflowTaskResponse>> {
        return __request(OpenAPI, {
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
    /**
     * Get Workflow Temporal Status
     * Get real-time status from Temporal for a workflow.
     *
     * Args:
     * workflow_id: The Temporal workflow ID (e.g., "dataset_ingestion-abc123")
     *
     * Returns:
     * Workflow status including current activity and progress from Temporal
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getWorkflowTemporalStatusApiV1WorkflowsWorkflowIdStatusGet({
        workflowId,
    }: {
        workflowId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/workflows/{workflow_id}/status',
            path: {
                'workflow_id': workflowId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Workflow
     * Cancel a running Temporal workflow.
     *
     * Args:
     * workflow_id: The workflow ID to cancel
     *
     * Returns:
     * Confirmation of cancellation request
     * @returns any Successful Response
     * @throws ApiError
     */
    public static cancelWorkflowApiV1WorkflowsWorkflowIdCancelPost({
        workflowId,
    }: {
        workflowId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/workflows/{workflow_id}/cancel',
            path: {
                'workflow_id': workflowId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
