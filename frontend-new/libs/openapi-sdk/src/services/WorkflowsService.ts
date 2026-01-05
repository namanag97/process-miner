/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowCreateRequest } from '../models/WorkflowCreateRequest';
import type { WorkflowResponse } from '../models/WorkflowResponse';
import type { WorkflowRunRequest } from '../models/WorkflowRunRequest';
import type { WorkflowRunResponse } from '../models/WorkflowRunResponse';
import type { WorkflowTemplate } from '../models/WorkflowTemplate';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class WorkflowsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Templates
     * List predefined workflow templates.
     * @returns WorkflowTemplate Successful Response
     * @throws ApiError
     */
    public listTemplatesApiV1WorkflowsTemplatesGet(): CancelablePromise<Array<WorkflowTemplate>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workflows/templates',
        });
    }
    /**
     * List Workflows
     * List all workflows.
     * @returns WorkflowResponse Successful Response
     * @throws ApiError
     */
    public listWorkflowsApiV1WorkflowsGet(): CancelablePromise<Array<WorkflowResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/workflows',
        });
    }
    /**
     * Create Workflow
     * Create a new workflow.
     * @param requestBody
     * @returns WorkflowResponse Successful Response
     * @throws ApiError
     */
    public createWorkflowApiV1WorkflowsPost(
        requestBody: WorkflowCreateRequest,
    ): CancelablePromise<WorkflowResponse> {
        return this.httpRequest.request({
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
     * Get workflow by ID.
     * @param workflowId
     * @returns WorkflowResponse Successful Response
     * @throws ApiError
     */
    public getWorkflowApiV1WorkflowsWorkflowIdGet(
        workflowId: string,
    ): CancelablePromise<WorkflowResponse> {
        return this.httpRequest.request({
            method: 'GET',
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
     * Delete Workflow
     * Delete a workflow.
     * @param workflowId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteWorkflowApiV1WorkflowsWorkflowIdDelete(
        workflowId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
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
     * @param workflowId
     * @param requestBody
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public runWorkflowApiV1WorkflowsWorkflowIdRunPost(
        workflowId: string,
        requestBody: WorkflowRunRequest,
    ): CancelablePromise<WorkflowRunResponse> {
        return this.httpRequest.request({
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
     * @param workflowId
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public listWorkflowRunsApiV1WorkflowsWorkflowIdRunsGet(
        workflowId: string,
    ): CancelablePromise<Array<WorkflowRunResponse>> {
        return this.httpRequest.request({
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
     * @param runId
     * @returns WorkflowRunResponse Successful Response
     * @throws ApiError
     */
    public getWorkflowRunApiV1WorkflowsRunsRunIdGet(
        runId: string,
    ): CancelablePromise<WorkflowRunResponse> {
        return this.httpRequest.request({
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
}
