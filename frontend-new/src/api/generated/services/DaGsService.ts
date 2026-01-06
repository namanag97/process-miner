/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CreateDefinitionRequest } from '../models/CreateDefinitionRequest';
import type { DefinitionListResponse } from '../models/DefinitionListResponse';
import type { DefinitionResponse } from '../models/DefinitionResponse';
import type { RunListResponse } from '../models/RunListResponse';
import type { RunResponse } from '../models/RunResponse';
import type { TemplateInfo } from '../models/TemplateInfo';
import type { TriggerRunRequest } from '../models/TriggerRunRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DaGsService {
    /**
     * Get Templates
     * List predefined DAG templates.
     *
     * Returns all available workflow templates that can be used
     * to trigger DAG runs without creating custom definitions.
     * @returns TemplateInfo Successful Response
     * @throws ApiError
     */
    public static getTemplatesApiV1DagsTemplatesGet(): CancelablePromise<Array<TemplateInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dags/templates',
        });
    }
    /**
     * Create Definition
     * Create a new DAG definition.
     *
     * Validates the DAG structure (no cycles, valid edges) and
     * stores it for later execution.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createDefinitionApiV1DagsDefinitionsPost({
        requestBody,
        xOrgId,
    }: {
        requestBody: CreateDefinitionRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dags/definitions',
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
     * List Definitions
     * List all DAG definitions.
     *
     * Returns all stored DAG definitions, optionally filtered to
     * only active (non-archived) ones.
     * @returns DefinitionListResponse Successful Response
     * @throws ApiError
     */
    public static listDefinitionsApiV1DagsDefinitionsGet({
        activeOnly = true,
    }: {
        /**
         * Only return active definitions
         */
        activeOnly?: boolean,
    }): CancelablePromise<DefinitionListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dags/definitions',
            query: {
                'active_only': activeOnly,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Definition
     * Get a DAG definition by ID.
     *
     * Returns the full definition including all steps and edges.
     * @returns DefinitionResponse Successful Response
     * @throws ApiError
     */
    public static getDefinitionApiV1DagsDefinitionsDefinitionIdGet({
        definitionId,
    }: {
        definitionId: string,
    }): CancelablePromise<DefinitionResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dags/definitions/{definition_id}',
            path: {
                'definition_id': definitionId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Trigger Run
     * Trigger a new DAG run.
     *
     * Starts execution of a DAG definition. The run will execute
     * asynchronously with steps processed by Celery workers.
     *
     * Provide either definition_id or definition_name.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static triggerRunApiV1DagsRunsPost({
        requestBody,
        xOrgId,
    }: {
        requestBody: TriggerRunRequest,
        xOrgId?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dags/runs',
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
     * List Runs
     * List DAG runs.
     *
     * Returns runs for the current user with optional filtering
     * by status and definition.
     * @returns RunListResponse Successful Response
     * @throws ApiError
     */
    public static listRunsApiV1DagsRunsGet({
        status,
        definitionId,
        page = 1,
        pageSize = 20,
        xOrgId,
    }: {
        /**
         * Filter by status
         */
        status?: (string | null),
        /**
         * Filter by definition
         */
        definitionId?: (string | null),
        page?: number,
        pageSize?: number,
        xOrgId?: (string | null),
    }): CancelablePromise<RunListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dags/runs',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'status': status,
                'definition_id': definitionId,
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Run
     * Get DAG run status.
     *
     * Returns the current status of a run including all step
     * statuses and timing information.
     * @returns RunResponse Successful Response
     * @throws ApiError
     */
    public static getRunApiV1DagsRunsRunIdGet({
        runId,
    }: {
        runId: string,
    }): CancelablePromise<RunResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dags/runs/{run_id}',
            path: {
                'run_id': runId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Run
     * Cancel a DAG run.
     *
     * Stops execution and marks all pending steps as cancelled.
     * Already completed steps are not affected.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static cancelRunApiV1DagsRunsRunIdCancelPost({
        runId,
        xOrgId,
    }: {
        runId: string,
        xOrgId?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/dags/runs/{run_id}/cancel',
            path: {
                'run_id': runId,
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
