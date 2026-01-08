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
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class ObjectCentricProcessMiningService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Upload Ocel
     * Upload an OCEL file (JSON, SQLite, or XML format).
     * @param formData
     * @param asyncMode
     * @param xOrgId
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public uploadOcelApiV1OcpmUploadPost(
        formData: Body_upload_ocel_api_v1_ocpm_upload_post,
        asyncMode: boolean = true,
        xOrgId?: (string | null),
    ): CancelablePromise<OCELLogResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/upload',
            headers: {
                'X-Org-Id': xOrgId,
            },
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
     * @param xOrgId
     * @returns OCELLogListResponse Successful Response
     * @throws ApiError
     */
    public listOcelLogsApiV1OcpmLogsGet(
        xOrgId?: (string | null),
    ): CancelablePromise<OCELLogListResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/logs',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Ocel Log
     * Get OCEL log details.
     * @param datasetId
     * @param xOrgId
     * @returns OCELLogResponse Successful Response
     * @throws ApiError
     */
    public getOcelLogApiV1OcpmDatasetsDatasetIdGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OCELLogResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}',
            path: {
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
     * Delete Ocel Log
     * Delete an OCEL log.
     * @param datasetId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteOcelLogApiV1OcpmDatasetsDatasetIdDelete(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/ocpm/datasets/{dataset_id}',
            path: {
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
     * Get Object Types
     * Get object types in an OCEL log.
     * @param datasetId
     * @param xOrgId
     * @returns OCELObjectTypeResponse Successful Response
     * @throws ApiError
     */
    public getObjectTypesApiV1OcpmDatasetsDatasetIdObjectTypesGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Array<OCELObjectTypeResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/object-types',
            path: {
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
     * Get Ocel Statistics
     * Get detailed statistics for an OCEL log.
     * @param datasetId
     * @param xOrgId
     * @returns OCELStatisticsResponse Successful Response
     * @throws ApiError
     */
    public getOcelStatisticsApiV1OcpmDatasetsDatasetIdStatisticsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OCELStatisticsResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/statistics',
            path: {
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
     * Discover Oc Petri Net
     * Discover Object-Centric Petri Net from an OCEL log.
     * @param requestBody
     * @param asyncMode
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public discoverOcPetriNetApiV1OcpmDiscoverPost(
        requestBody: DiscoverOCPNRequest,
        asyncMode: boolean = true,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/discover',
            headers: {
                'X-Org-Id': xOrgId,
            },
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
     * @param xOrgId
     * @returns OCPetriNetResponse Successful Response
     * @throws ApiError
     */
    public listOcPetriNetsApiV1OcpmModelsGet(
        xOrgId?: (string | null),
    ): CancelablePromise<Array<OCPetriNetResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/models',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Oc Petri Net
     * Get Object-Centric Petri Net details.
     * @param modelId
     * @param xOrgId
     * @returns OCPetriNetResponse Successful Response
     * @throws ApiError
     */
    public getOcPetriNetApiV1OcpmModelsModelIdGet(
        modelId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OCPetriNetResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/models/{model_id}',
            path: {
                'model_id': modelId,
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
     * Delete Oc Petri Net
     * Delete an Object-Centric Petri Net.
     * @param modelId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteOcPetriNetApiV1OcpmModelsModelIdDelete(
        modelId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/v1/ocpm/models/{model_id}',
            path: {
                'model_id': modelId,
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
     * Get Object Relationships
     * Get object-event relationships summary.
     * @param datasetId
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getObjectRelationshipsApiV1OcpmDatasetsDatasetIdRelationshipsGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/relationships',
            path: {
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
     * Get Oc Dfg
     * Get Object-Centric Directly-Follows Graph (OC-DFG).
     * @param datasetId
     * @param xOrgId
     * @returns OCDFGResponse Successful Response
     * @throws ApiError
     */
    public getOcDfgApiV1OcpmDatasetsDatasetIdOcDfgGet(
        datasetId: string,
        xOrgId?: (string | null),
    ): CancelablePromise<OCDFGResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ocpm/datasets/{dataset_id}/oc-dfg',
            path: {
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
     * Flatten an OCEL log to a traditional event log based on an object type.
     * @param datasetId
     * @param formData
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public flattenOcelToDatasetApiV1OcpmDatasetsDatasetIdFlattenPost(
        datasetId: string,
        formData: Body_flatten_ocel_to_dataset_api_v1_ocpm_datasets__dataset_id__flatten_post,
        xOrgId?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ocpm/datasets/{dataset_id}/flatten',
            path: {
                'dataset_id': datasetId,
            },
            headers: {
                'X-Org-Id': xOrgId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
