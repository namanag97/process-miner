/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelResponse } from '../models/CancelResponse';
import type { OperationListResponse } from '../models/OperationListResponse';
import type { OperationStatus } from '../models/OperationStatus';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class OperationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Operation Status
     * Get operation status from Temporal.
     *
     * This is the ONLY place to get job/workflow status.
     * Queries Temporal directly - no database status polling.
     *
     * Workflow ID Patterns:
     * - Ingestion: ingest-dataset-{dataset_id}
     * - Validation: validate-dataset-{dataset_id}
     * - Discovery: discover-{dataset_id}-{miner_type}
     * - Conformance: conformance-{dataset_id}-{model_id}
     *
     * Args:
     * workflow_id: The Temporal workflow ID
     *
     * Returns:
     * OperationStatus with current status and progress
     * @param workflowId
     * @param xOrgId
     * @returns OperationStatus Successful Response
     * @throws ApiError
     */
    public getOperationStatusApiV1OperationsWorkflowIdGet(
        workflowId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OperationStatus> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/operations/{workflow_id}',
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
     * List Operations
     * List operations from Temporal.
     *
     * Note: Temporal list queries may be slower than database queries.
     * For high-frequency list access, consider using the Workflow read-model.
     *
     * Args:
     * entity_type: Filter by entity type
     * entity_id: Filter by entity ID
     * status: Filter by status
     * limit: Maximum results
     * offset: Pagination offset
     *
     * Returns:
     * List of operations matching filters
     * @param entityType Filter by entity type (dataset, model)
     * @param entityId Filter by entity ID
     * @param status Filter by status (RUNNING, COMPLETED, FAILED)
     * @param limit
     * @param offset
     * @param xOrgId
     * @returns OperationListResponse Successful Response
     * @throws ApiError
     */
    public listOperationsApiV1OperationsGet(
        entityType?: (string | null),
        entityId?: (string | null),
        status?: (string | null),
        limit: number = 20,
        offset?: number,
        xOrgId?: (string | null),
    ): CancelablePromise<OperationListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/operations',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'entity_type': entityType,
                'entity_id': entityId,
                'status': status,
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Cancel Operation
     * Cancel a running operation.
     *
     * Sends cancel request to Temporal. The workflow will receive a
     * CancelledError and should perform cleanup.
     *
     * Args:
     * workflow_id: The operation to cancel
     *
     * Returns:
     * Confirmation of cancel request
     * @param workflowId
     * @param xOrgId
     * @returns CancelResponse Successful Response
     * @throws ApiError
     */
    public cancelOperationApiV1OperationsWorkflowIdCancelPost(
        workflowId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<CancelResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/operations/{workflow_id}/cancel',
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
     * Get Operation Result
     * Get the final result of a completed operation.
     *
     * Only available for COMPLETED workflows.
     *
     * Args:
     * workflow_id: The operation ID
     *
     * Returns:
     * The workflow's return value
     * @param workflowId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getOperationResultApiV1OperationsWorkflowIdResultGet(
        workflowId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/operations/{workflow_id}/result',
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
     * Stream Operation Progress
     * Stream real-time workflow progress via Server-Sent Events.
     *
     * This endpoint provides real-time updates for long-running operations like:
     * - Dataset ingestion (ingest-dataset-{uuid})
     * - Process discovery (discover-{uuid}-{miner})
     * - Conformance checking (conformance-{uuid}-{uuid})
     *
     * ## Event Types
     *
     * The stream emits the following SSE event types:
     *
     * - `step:started` - Activity step has started
     * - `step:progress` - Progress update within a step (0-100%)
     * - `step:completed` - Activity step completed successfully
     * - `step:failed` - Activity step failed
     * - `workflow:completed` - Entire workflow completed
     * - `workflow:failed` - Entire workflow failed
     *
     * ## Event Data Format
     *
     * ```json
     * {
         * "workflow_id": "ingest-dataset-abc123",
         * "event": "step:progress",
         * "step": "parse_to_parquet",
         * "progress": 45,
         * "timestamp": "2024-01-15T10:30:00Z",
         * "details": {
             * "phase": "converting_events",
             * "total_events": 10000
             * }
             * }
             * ```
             *
             * ## Frontend Usage
             *
             * ```javascript
             * const eventSource = new EventSource('/api/v1/operations/ingest-dataset-123/stream');
             *
             * eventSource.addEventListener('step:progress', (event) => {
                 * const data = JSON.parse(event.data);
                 * updateProgressBar(data.progress);
                 * showStatus(`${data.step}: ${data.details.phase}`);
                 * });
                 *
                 * eventSource.addEventListener('workflow:completed', (event) => {
                     * showSuccess('Operation completed!');
                     * eventSource.close();
                     * });
                     *
                     * eventSource.addEventListener('workflow:failed', (event) => {
                         * const data = JSON.parse(event.data);
                         * showError(data.details.error);
                         * eventSource.close();
                         * });
                         *
                         * eventSource.onerror = () => {
                             * // Reconnect logic
                             * };
                             * ```
                             *
                             * ## Connection Behavior
                             *
                             * - Sends initial state from Temporal query on connect
                             * - Subscribes to Redis pub/sub for real-time updates
                             * - Sends heartbeat every 15 seconds to keep connection alive
                             * - Automatically closes when workflow completes or fails
                             * - Client should handle reconnection for network issues
                             *
                             * Args:
                             * workflow_id: The Temporal workflow ID (e.g., "ingest-dataset-{uuid}")
                             *
                             * Returns:
                             * SSE stream with progress events
                             * @param workflowId
                             * @param xOrgId
                             * @returns any Successful Response
                             * @throws ApiError
                             */
                            public streamOperationProgressApiV1OperationsWorkflowIdStreamGet(
                                workflowId: string,
                                xOrgId?: (string | null),
                            ): CancelablePromise<any> {
                                return this.httpRequest.request({
                                    method: 'GET',
                                    url: '/api/v1/operations/{workflow_id}/stream',
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
