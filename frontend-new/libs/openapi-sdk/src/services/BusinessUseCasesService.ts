/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class BusinessUseCasesService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Detect P2P Mavericks
     * Detect maverick purchasing behavior in P2P process.
     * @param datasetId
     * @param referenceModelId
     * @param threshold Fitness threshold (0-1)
     * @returns any Successful Response
     * @throws ApiError
     */
    public detectP2PMavericksApiV1BusinessP2PMavericksDatasetIdReferenceModelIdGet(
        datasetId: string,
        referenceModelId: string,
        threshold: number = 0.8,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/business/p2p/mavericks/{dataset_id}/{reference_model_id}',
            path: {
                'dataset_id': datasetId,
                'reference_model_id': referenceModelId,
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
     * Generate P2P Audit Report
     * Generate comprehensive P2P audit report.
     * @param datasetId
     * @param referenceModelId
     * @returns any Successful Response
     * @throws ApiError
     */
    public generateP2PAuditReportApiV1BusinessP2PAuditReportDatasetIdReferenceModelIdGet(
        datasetId: string,
        referenceModelId: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/business/p2p/audit-report/{dataset_id}/{reference_model_id}',
            path: {
                'dataset_id': datasetId,
                'reference_model_id': referenceModelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Split Log By Attribute
     * Split event log by attribute for comparative analysis.
     * @param datasetId
     * @param attribute Attribute to split on
     * @param value Value to filter for
     * @returns any Successful Response
     * @throws ApiError
     */
    public splitLogByAttributeApiV1BusinessO2CSplitLogDatasetIdGet(
        datasetId: string,
        attribute: string,
        value: string,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/business/o2c/split-log/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'attribute': attribute,
                'value': value,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Compare Process Variants
     * Compare process variants between two logs.
     * @param datasetId1
     * @param datasetId2
     * @param log1Name
     * @param log2Name
     * @returns any Successful Response
     * @throws ApiError
     */
    public compareProcessVariantsApiV1BusinessO2CCompareDatasetId1DatasetId2Get(
        datasetId1: string,
        datasetId2: string,
        log1Name: string = 'Group A',
        log2Name: string = 'Group B',
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/business/o2c/compare/{dataset_id1}/{dataset_id2}',
            path: {
                'dataset_id1': datasetId1,
                'dataset_id2': datasetId2,
            },
            query: {
                'log1_name': log1Name,
                'log2_name': log2Name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Simulate Process Changes
     * Simulate process changes using Monte Carlo simulation.
     * @param datasetId
     * @param activityDurationReduction Activity duration reduction (0-1)
     * @param capacityIncrease Capacity increase (0-1)
     * @param numSimulations Number of Monte Carlo iterations
     * @returns any Successful Response
     * @throws ApiError
     */
    public simulateProcessChangesApiV1BusinessSupplyChainSimulateDatasetIdPost(
        datasetId: string,
        activityDurationReduction?: number,
        capacityIncrease?: number,
        numSimulations: number = 1000,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/business/supply-chain/simulate/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'activity_duration_reduction': activityDurationReduction,
                'capacity_increase': capacityIncrease,
                'num_simulations': numSimulations,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Detect Journey Dropoffs
     * Detect drop-offs in customer journey funnel.
     * @param datasetId
     * @param expectedPath Expected journey path (comma-separated)
     * @returns any Successful Response
     * @throws ApiError
     */
    public detectJourneyDropoffsApiV1BusinessCustomerJourneyDropoffsDatasetIdGet(
        datasetId: string,
        expectedPath?: (string | null),
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/business/customer-journey/dropoffs/{dataset_id}',
            path: {
                'dataset_id': datasetId,
            },
            query: {
                'expected_path': expectedPath,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
