/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_flatten_ocel_to_dataset_api_v1_ocpm_logs__log_id__flatten_post } from '../models/Body_flatten_ocel_to_dataset_api_v1_ocpm_logs__log_id__flatten_post';
import type { Body_upload_ocel_api_v1_ocpm_upload_post } from '../models/Body_upload_ocel_api_v1_ocpm_upload_post';
import type { DiscoverOCPNRequest } from '../models/DiscoverOCPNRequest';
import type { OCDFGResponse } from '../models/OCDFGResponse';
import type { OCELLogListResponse } from '../models/OCELLogListResponse';
import type { OCELLogResponse } from '../models/OCELLogResponse';
import type { OCELObjectTypeResponse } from '../models/OCELObjectTypeResponse';
import type { OCELStatisticsResponse } from '../models/OCELStatisticsResponse';
import type { OCPetriNetResponse } from '../models/OCPetriNetResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ObjectCentricProcessMiningService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Upload Ocel
     * Upload an OCEL file (JSON, SQLite, or XML format).
     *
     * BUG-025 FIX: OCEL 2.0 table population is now deferred to background by default.
     *
     * Supports OCEL 2.0 standard formats:
     * - `.jsonocel` - JSON format
     * - `.sqlite` - SQLite database format
     * - `.xmlocel` - XML format
     * @param formData
     * @param asyncMode
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public uploadOcelApiV1OcpmUploadPost(
        formData: Body_upload_ocel_api_v1_ocpm_upload_post,
        asyncMode: boolean = true,
    ): CancelablePromise<OCELLogResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/upload',
            query: {
                'async_mode': asyncMode,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Ocel Logs
     * List all OCEL logs.
     *
     * Returns a list of all uploaded object-centric event logs with their metadata.
     * @returns OCELLogListResponse Successful Response
     * @throws ApiError
     */
    public listOcelLogsApiV1OcpmLogsGet(): CancelablePromise<OCELLogListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs',
        });
    }
    /**
     * Get Ocel Log
     * Get OCEL log details.
     *
     * Returns detailed information about a specific object-centric event log.
     * @param logId
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public getOcelLogApiV1OcpmLogsLogIdGet(
        logId: string,
    ): CancelablePromise<OCELLogResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs/{log_id}',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Ocel Log
     * Delete an OCEL log.
     *
     * Removes the log and all associated data (object types, models).
     * @param logId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteOcelLogApiV1OcpmLogsLogIdDelete(
        logId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/ocpm/logs/{log_id}',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Object Types
     * Get object types in an OCEL log.
     *
     * Returns all object types (e.g., Order, Item, Package) with their counts.
     * @param logId
     * @returns OCELObjectTypeResponse Successful Response
     * @throws ApiError
     */
    public getObjectTypesApiV1OcpmLogsLogIdObjectTypesGet(
        logId: string,
    ): CancelablePromise<Array<OCELObjectTypeResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs/{log_id}/object-types',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Ocel Statistics
     * Get detailed statistics for an OCEL log.
     *
     * Returns comprehensive statistics including event counts, object counts,
     * activities, and objects per type.
     * @param logId
     * @returns OCELStatisticsResponse Successful Response
     * @throws ApiError
     */
    public getOcelStatisticsApiV1OcpmLogsLogIdStatisticsGet(
        logId: string,
    ): CancelablePromise<OCELStatisticsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs/{log_id}/statistics',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Discover Oc Petri Net
     * Discover Object-Centric Petri Net from an OCEL log.
     *
     * BUG-027 FIX: Heavy OC-PN discovery is now offloaded to background by default.
     * Uses PM4Py's `discover_oc_petri_net()` to create an OC-PN that captures
     * the process behavior across all object types.
     * @param requestBody
     * @param asyncMode
     * @returns any Successful Response
     * @throws ApiError
     */
    public discoverOcPetriNetApiV1OcpmDiscoverPost(
        requestBody: DiscoverOCPNRequest,
        asyncMode: boolean = true,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/discover',
            query: {
                'async_mode': asyncMode,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Oc Petri Nets
     * List all discovered Object-Centric Petri Nets.
     * @returns OCPetriNetResponse Successful Response
     * @throws ApiError
     */
    public listOcPetriNetsApiV1OcpmModelsGet(): CancelablePromise<Array<OCPetriNetResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/models',
        });
    }
    /**
     * Get Oc Petri Net
     * Get Object-Centric Petri Net details.
     * @param modelId
     * @returns OCPetriNetResponse Successful Response
     * @throws ApiError
     */
    public getOcPetriNetApiV1OcpmModelsModelIdGet(
        modelId: string,
    ): CancelablePromise<OCPetriNetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/models/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Oc Petri Net
     * Delete an Object-Centric Petri Net.
     * @param modelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteOcPetriNetApiV1OcpmModelsModelIdDelete(
        modelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/ocpm/models/{model_id}',
            path: {
                'model_id': modelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Object Relationships
     * Get object-event relationships summary.
     *
     * Shows how many events and cases are associated with each object type.
     * This is stored metadata from the upload - actual graph requires re-parsing.
     * @param logId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getObjectRelationshipsApiV1OcpmLogsLogIdRelationshipsGet(
        logId: string,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs/{log_id}/relationships',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Oc Dfg
     * Get Object-Centric Directly-Follows Graph (OC-DFG) for an OCEL log.
     *
     * Computes the OC-DFG using PM4Py's `ocel_discover_ocdfg()` function.
     * Returns separate DFG graphs for each object type, showing how activities
     * relate to each other within the context of different object types.
     *
     * This endpoint requires the OCEL data to be stored (uploaded after Phase 2.1).
     * @param logId
     * @returns OCDFGResponse Successful Response
     * @throws ApiError
     */
    public getOcDfgApiV1OcpmLogsLogIdOcDfgGet(
        logId: string,
    ): CancelablePromise<OCDFGResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs/{log_id}/oc-dfg',
            path: {
                'log_id': logId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Supported Formats
     * List supported OCEL file formats.
     * @returns any Successful Response
     * @throws ApiError
     */
    public listSupportedFormatsApiV1OcpmFormatsGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/formats',
        });
    }
    /**
     * Flatten Ocel To Dataset
     * Flatten an OCEL log to a traditional event log (Dataset) based on an object type.
     *
     * Job-Centric Architecture: Returns 202 with job_id for progress tracking.
     *
     * This operation:
     * 1. Takes an OCEL log and flattens it by a specific object type
     * 2. Creates a new Dataset entity with the flattened events
     * 3. Returns a job_id for tracking the background processing
     *
     * Example: Flattening an e-commerce OCEL on 'Order' creates a traditional
     * event log where each Order becomes a case.
     * @param logId
     * @param formData
     * @returns any Successful Response
     * @throws ApiError
     */
    public flattenOcelToDatasetApiV1OcpmLogsLogIdFlattenPost(
        logId: string,
        formData: Body_flatten_ocel_to_dataset_api_v1_ocpm_logs__log_id__flatten_post,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/logs/{log_id}/flatten',
            path: {
                'log_id': logId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
