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
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ConformanceService {
    /**
     * Check Conformance
     * Check conformance between an event log and a process model.
     * @returns ConformanceResponse Successful Response
     * @throws ApiError
     */
    public static checkConformanceApiV1ConformanceCheckPost({
        requestBody,
        autoDiscover = false,
    }: {
        requestBody: ConformanceCheckRequest,
        /**
         * Auto-discover model if model_id not provided
         */
        autoDiscover?: boolean,
    }): CancelablePromise<ConformanceResponse> {
        return __request(OpenAPI, {
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
     * @returns ConformanceListResponse Successful Response
     * @throws ApiError
     */
    public static listConformanceResultsApiV1ConformanceResultsGet({
        datasetId,
        modelId,
        page = 1,
        pageSize = 20,
    }: {
        datasetId?: (string | null),
        modelId?: (string | null),
        page?: number,
        pageSize?: number,
    }): CancelablePromise<ConformanceListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/results',
            query: {
                'dataset_id': datasetId,
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
     * @returns ConformanceResponse Successful Response
     * @throws ApiError
     */
    public static getConformanceResultApiV1ConformanceResultsResultIdGet({
        resultId,
    }: {
        resultId: string,
    }): CancelablePromise<ConformanceResponse> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteConformanceResultApiV1ConformanceResultsResultIdDelete({
        resultId,
    }: {
        resultId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns DiagnosticsResponse Successful Response
     * @throws ApiError
     */
    public static getConformanceDiagnosticsApiV1ConformanceDiagnosticsDatasetIdModelIdGet({
        datasetId,
        modelId,
    }: {
        datasetId: string,
        modelId: string,
    }): CancelablePromise<DiagnosticsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/diagnostics/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns DeviationResponse Successful Response
     * @throws ApiError
     */
    public static getDeviationsApiV1ConformanceDeviationsDatasetIdModelIdGet({
        datasetId,
        modelId,
        threshold = 0.8,
    }: {
        datasetId: string,
        modelId: string,
        threshold?: number,
    }): CancelablePromise<Array<DeviationResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/deviations/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns AlignmentDiagnosticsResponse Successful Response
     * @throws ApiError
     */
    public static getAlignmentDiagnosticsApiV1ConformanceAlignmentsDatasetIdModelIdGet({
        datasetId,
        modelId,
        maxCases = 100,
    }: {
        datasetId: string,
        modelId: string,
        maxCases?: number,
    }): CancelablePromise<AlignmentDiagnosticsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/alignments/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
    public static listConformanceMethodsApiV1ConformanceMethodsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/methods',
        });
    }
    /**
     * Get Quality Metrics
     * Get full quality metrics for a log-model pair (fitness, precision, generalization, simplicity).
     * @returns QualityMetricsResponse Successful Response
     * @throws ApiError
     */
    public static getQualityMetricsApiV1ConformanceQualityDatasetIdModelIdGet({
        datasetId,
        modelId,
    }: {
        datasetId: string,
        modelId: string,
    }): CancelablePromise<QualityMetricsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/quality/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static importReferenceModelApiV1ConformanceImportModelPost({
        projectId,
        modelName,
        modelContent,
    }: {
        /**
         * Project ID to store the model under
         */
        projectId: string,
        /**
         * Name for the imported model
         */
        modelName: string,
        /**
         * XML content (PNML or BPMN)
         */
        modelContent: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRootCauseAnalysisApiV1ConformanceRootCauseDatasetIdModelIdGet({
        datasetId,
        modelId,
        attributes = 'resource',
    }: {
        datasetId: string,
        modelId: string,
        /**
         * Comma-separated list of attributes to analyze
         */
        attributes?: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/root-cause/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDeviationsByActivityApiV1ConformanceDeviationsByActivityDatasetIdModelIdGet({
        datasetId,
        modelId,
    }: {
        datasetId: string,
        modelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/deviations/by-activity/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getDeviationsByPositionApiV1ConformanceDeviationsByPositionDatasetIdModelIdGet({
        datasetId,
        modelId,
    }: {
        datasetId: string,
        modelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/deviations/by-position/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAttributeCorrelationApiV1ConformanceDeviationsAttributeCorrelationDatasetIdModelIdGet({
        datasetId,
        modelId,
        attribute = 'resource',
    }: {
        datasetId: string,
        modelId: string,
        /**
         * Attribute to analyze
         */
        attribute?: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/conformance/deviations/attribute-correlation/{dataset_id}/{model_id}',
            path: {
                'dataset_id': datasetId,
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
