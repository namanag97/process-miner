/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AlignmentDiagnosticsResponse } from '../models/AlignmentDiagnosticsResponse';
import type { ConformanceCheckRequest } from '../models/ConformanceCheckRequest';
import type { ConformanceListResponse } from '../models/ConformanceListResponse';
import type { ConformanceResponse } from '../models/ConformanceResponse';
import type { DeviationResponse } from '../models/DeviationResponse';
import type { DiagnosticsResponse } from '../models/DiagnosticsResponse';
import type { QualityMetricsResponse } from '../models/QualityMetricsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ConformanceService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Check Conformance
     * Check conformance between an event log and a process model.
     *
     * Supports two methods:
     * - `token_replay`: Fast, token-based replay (default)
     * - `alignment`: More accurate, alignment-based (slower)
     *
     * Job-Centric Architecture Enhancement:
     * - If `auto_discover=True` and no model_id, first runs discovery then conformance
     * - Returns 202 with chained job IDs for async processing
     *
     * Returns fitness, precision, and conformance status.
     * @param requestBody
     * @param autoDiscover Auto-discover model if model_id not provided
     * @returns ConformanceResponse Successful Response
     * @throws ApiError
     */
    public checkConformanceApiV1ConformanceCheckPost(
        requestBody: ConformanceCheckRequest,
        autoDiscover: boolean = false,
    ): CancelablePromise<ConformanceResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/conformance/check',
            query: {
                'auto_discover': autoDiscover,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Conformance Results
     * List conformance check results.
     *
     * Optionally filter by log_id or model_id.
     * @param logId Filter by event log ID
     * @param modelId Filter by model ID
     * @param page
     * @param pageSize
     * @returns ConformanceListResponse Successful Response
     * @throws ApiError
     */
    public listConformanceResultsApiV1ConformanceResultsGet(
        logId?: (string | null),
        modelId?: (string | null),
        page: number = 1,
        pageSize: number = 20,
    ): CancelablePromise<ConformanceListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/results',
            query: {
                'log_id': logId,
                'model_id': modelId,
                'page': page,
                'page_size': pageSize,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Conformance Result
     * Get a specific conformance check result.
     * @param resultId
     * @returns ConformanceResponse Successful Response
     * @throws ApiError
     */
    public getConformanceResultApiV1ConformanceResultsResultIdGet(
        resultId: string,
    ): CancelablePromise<ConformanceResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/results/{result_id}',
            path: {
                'result_id': resultId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Conformance Result
     * Delete a conformance check result.
     * @param resultId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteConformanceResultApiV1ConformanceResultsResultIdDelete(
        resultId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/conformance/results/{result_id}',
            path: {
                'result_id': resultId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Conformance Diagnostics
     * Get detailed conformance diagnostics for a log-model pair.
     *
     * Returns trace-level analysis including deviations.
     * @param logId
     * @param modelId
     * @returns DiagnosticsResponse Successful Response
     * @throws ApiError
     */
    public getConformanceDiagnosticsApiV1ConformanceDiagnosticsLogIdModelIdGet(
        logId: string,
        modelId: string,
    ): CancelablePromise<DiagnosticsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/diagnostics/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Deviations
     * Detect and list specific deviations from the model.
     *
     * Returns case-level deviation information.
     * @param logId
     * @param modelId
     * @param threshold
     * @returns DeviationResponse Successful Response
     * @throws ApiError
     */
    public getDeviationsApiV1ConformanceDeviationsLogIdModelIdGet(
        logId: string,
        modelId: string,
        threshold: number = 0.8,
    ): CancelablePromise<Array<DeviationResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/deviations/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            query: {
                'threshold': threshold,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Alignment Diagnostics
     * Get detailed alignment diagnostics for a log-model pair.
     *
     * Uses PM4Py's alignment-based conformance checking to compute optimal
     * alignments between traces and the process model. This provides:
     * - Per-case fitness scores
     * - Detailed alignment moves (sync, log-only, model-only)
     * - Identification of deviating activities
     *
     * Note: This is computationally expensive for large logs. Use max_cases to limit.
     * @param logId
     * @param modelId
     * @param maxCases Max cases to include
     * @returns AlignmentDiagnosticsResponse Successful Response
     * @throws ApiError
     */
    public getAlignmentDiagnosticsApiV1ConformanceAlignmentsLogIdModelIdGet(
        logId: string,
        modelId: string,
        maxCases: number = 100,
    ): CancelablePromise<AlignmentDiagnosticsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/alignments/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            query: {
                'max_cases': maxCases,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Conformance Methods
     * List available conformance checking methods.
     * @returns any Successful Response
     * @throws ApiError
     */
    public listConformanceMethodsApiV1ConformanceMethodsGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/methods',
        });
    }
    /**
     * Get Quality Metrics
     * Get full quality metrics for a log-model pair.
     *
     * Returns all 4 quality dimensions from PM4py:
     * - **Fitness**: How well the log fits the model (0-1)
     * - **Precision**: How much the model allows for behavior not observed in log (0-1)
     * - **Generalization**: How well the model generalizes beyond observed behavior (0-1)
     * - **Simplicity**: How simple/understandable the model is (0-1)
     * - **F-score**: Harmonic mean of fitness and precision
     *
     * All metrics are higher-is-better.
     * @param logId
     * @param modelId
     * @returns QualityMetricsResponse Successful Response
     * @throws ApiError
     */
    public getQualityMetricsApiV1ConformanceQualityLogIdModelIdGet(
        logId: string,
        modelId: string,
    ): CancelablePromise<QualityMetricsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/quality/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Reference Model
     * Import a reference model from PNML or BPMN format.
     *
     * Phase 11.1 - Reference Model Management
     *
     * Supports:
     * - PNML (Petri Net Markup Language) - direct import
     * - BPMN 2.0 (Business Process Model and Notation) - imported and converted to Petri net
     *
     * Use this to upload external reference models for conformance checking.
     *
     * Args:
     * project_id: The project to associate the model with
     * model_name: Display name for the model
     * model_content: XML content of the PNML or BPMN file
     *
     * Returns:
     * Created process model with ID
     * @param projectId Project ID to store the model under
     * @param modelName Name for the imported model
     * @param modelContent XML content (PNML or BPMN)
     * @returns any Successful Response
     * @throws ApiError
     */
    public importReferenceModelApiV1ConformanceImportModelPost(
        projectId: string,
        modelName: string,
        modelContent: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/conformance/import-model',
            query: {
                'project_id': projectId,
                'model_name': modelName,
                'model_content': modelContent,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Root Cause Analysis
     * Get comprehensive root cause analysis for conformance deviations.
     *
     * Phase 11.3 - Root Cause Analysis
     *
     * Analyzes:
     * - Deviation aggregation by activity (which activities cause most issues)
     * - Deviation aggregation by position (where in the process do issues occur)
     * - Attribute correlation (which resources/departments have more deviations)
     *
     * Use this to identify patterns in conformance violations.
     *
     * Args:
     * log_id: Event log ID
     * model_id: Process model ID
     * attributes: Comma-separated attributes to analyze (default: "resource")
     *
     * Returns:
     * Comprehensive root cause analysis report
     * @param logId
     * @param modelId
     * @param attributes Comma-separated list of attributes to analyze (e.g., 'resource,department')
     * @returns any Successful Response
     * @throws ApiError
     */
    public getRootCauseAnalysisApiV1ConformanceRootCauseLogIdModelIdGet(
        logId: string,
        modelId: string,
        attributes: string = 'resource',
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/root-cause/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            query: {
                'attributes': attributes,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Deviations By Activity
     * Get deviation aggregation by activity.
     *
     * Identifies which activities cause the most conformance issues.
     * @param logId
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDeviationsByActivityApiV1ConformanceDeviationsByActivityLogIdModelIdGet(
        logId: string,
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/deviations/by-activity/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Deviations By Position
     * Get deviation aggregation by position in trace.
     *
     * Identifies at which point in the process deviations occur most frequently.
     * @param logId
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getDeviationsByPositionApiV1ConformanceDeviationsByPositionLogIdModelIdGet(
        logId: string,
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/deviations/by-position/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Attribute Correlation
     * Analyze correlation between case attributes and conformance deviations.
     *
     * Identifies which attribute values (e.g., specific resources or departments)
     * are associated with more conformance violations.
     * @param logId
     * @param modelId
     * @param attribute Attribute to analyze (e.g., resource, department)
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAttributeCorrelationApiV1ConformanceDeviationsAttributeCorrelationLogIdModelIdGet(
        logId: string,
        modelId: string,
        attribute: string = 'resource',
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/conformance/deviations/attribute-correlation/{log_id}/{model_id}',
            path: {
                'log_id': logId,
                'model_id': modelId,
            },
            query: {
                'attribute': attribute,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
