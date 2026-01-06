/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_flatten_ocel_to_dataset_api_v1_ocpm_datasets__dataset_id__flatten_post } from '../models/Body_flatten_ocel_to_dataset_api_v1_ocpm_datasets__dataset_id__flatten_post';
import type { Body_upload_ocel_api_v1_ocpm_upload_post } from '../models/Body_upload_ocel_api_v1_ocpm_upload_post';
import type { DiscoverOCPNRequest } from '../models/DiscoverOCPNRequest';
import type { OCDFGResponse } from '../models/OCDFGResponse';
import type { OCELLogListResponse } from '../models/OCELLogListResponse';
import type { OCELLogResponse } from '../models/OCELLogResponse';
import type { OCELObjectTypeResponse } from '../models/OCELObjectTypeResponse';
import type { OCELStatisticsResponse } from '../models/OCELStatisticsResponse';
import type { OCPetriNetResponse } from '../models/OCPetriNetResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ObjectCentricProcessMiningService {
    /**
     * Upload Ocel
     * Upload an OCEL file (JSON, SQLite, or XML format).
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public static uploadOcelApiV1OcpmUploadPost({
        formData,
        asyncMode = true,
    }: {
        formData: Body_upload_ocel_api_v1_ocpm_upload_post,
        asyncMode?: boolean,
    }): CancelablePromise<OCELLogResponse> {
        return __request(OpenAPI, {
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
     * @returns OCELLogListResponse Successful Response
     * @throws ApiError
     */
    public static listOcelLogsApiV1OcpmLogsGet(): CancelablePromise<OCELLogListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/logs',
        });
    }
    /**
     * Get Ocel Log
     * Get OCEL log details.
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public static getOcelLogApiV1OcpmDatasetsDatasetIdGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<OCELLogResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Ocel Log
     * Delete an OCEL log.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteOcelLogApiV1OcpmDatasetsDatasetIdDelete({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/v1/ocpm/datasets/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Object Types
     * Get object types in an OCEL log.
     * @returns OCELObjectTypeResponse Successful Response
     * @throws ApiError
     */
    public static getObjectTypesApiV1OcpmDatasetsDatasetIdObjectTypesGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<Array<OCELObjectTypeResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/object-types',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Ocel Statistics
     * Get detailed statistics for an OCEL log.
     * @returns OCELStatisticsResponse Successful Response
     * @throws ApiError
     */
    public static getOcelStatisticsApiV1OcpmDatasetsDatasetIdStatisticsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<OCELStatisticsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/statistics',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Discover Oc Petri Net
     * Discover Object-Centric Petri Net from an OCEL log.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static discoverOcPetriNetApiV1OcpmDiscoverPost({
        requestBody,
        asyncMode = true,
    }: {
        requestBody: DiscoverOCPNRequest,
        asyncMode?: boolean,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
    public static listOcPetriNetsApiV1OcpmModelsGet(): CancelablePromise<Array<OCPetriNetResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/models',
        });
    }
    /**
     * Get Oc Petri Net
     * Get Object-Centric Petri Net details.
     * @returns OCPetriNetResponse Successful Response
     * @throws ApiError
     */
    public static getOcPetriNetApiV1OcpmModelsModelIdGet({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<OCPetriNetResponse> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteOcPetriNetApiV1OcpmModelsModelIdDelete({
        modelId,
    }: {
        modelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getObjectRelationshipsApiV1OcpmDatasetsDatasetIdRelationshipsGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/relationships',
            path: {
                'dataset_id': datasetId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Oc Dfg
     * Get Object-Centric Directly-Follows Graph (OC-DFG).
     * @returns OCDFGResponse Successful Response
     * @throws ApiError
     */
    public static getOcDfgApiV1OcpmDatasetsDatasetIdOcDfgGet({
        datasetId,
    }: {
        datasetId: string,
    }): CancelablePromise<OCDFGResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/oc-dfg',
            path: {
                'dataset_id': datasetId,
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
    public static listSupportedFormatsApiV1OcpmFormatsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/ocpm/formats',
        });
    }
    /**
     * Flatten Ocel To Dataset
     * Flatten an OCEL log to a traditional event log based on an object type.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static flattenOcelToDatasetApiV1OcpmDatasetsDatasetIdFlattenPost({
        datasetId,
        formData,
    }: {
        datasetId: string,
        formData: Body_flatten_ocel_to_dataset_api_v1_ocpm_datasets__dataset_id__flatten_post,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/ocpm/datasets/{dataset_id}/flatten',
            path: {
                'dataset_id': datasetId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
