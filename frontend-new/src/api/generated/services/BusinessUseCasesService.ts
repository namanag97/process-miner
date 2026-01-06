/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class BusinessUseCasesService {
    /**
     * Detect P2P Mavericks
     * Detect maverick purchasing behavior in P2P process.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static detectP2PMavericksApiV1BusinessP2PMavericksDatasetIdReferenceModelIdGet({
        datasetId,
        referenceModelId,
        threshold = 0.8,
    }: {
        datasetId: string,
        referenceModelId: string,
        /**
         * Fitness threshold (0-1)
         */
        threshold?: number,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static generateP2PAuditReportApiV1BusinessP2PAuditReportDatasetIdReferenceModelIdGet({
        datasetId,
        referenceModelId,
    }: {
        datasetId: string,
        referenceModelId: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static splitLogByAttributeApiV1BusinessO2CSplitLogDatasetIdGet({
        datasetId,
        attribute,
        value,
    }: {
        datasetId: string,
        /**
         * Attribute to split on
         */
        attribute: string,
        /**
         * Value to filter for
         */
        value: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static compareProcessVariantsApiV1BusinessO2CCompareDatasetId1DatasetId2Get({
        datasetId1,
        datasetId2,
        log1Name = 'Group A',
        log2Name = 'Group B',
    }: {
        datasetId1: string,
        datasetId2: string,
        log1Name?: string,
        log2Name?: string,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static simulateProcessChangesApiV1BusinessSupplyChainSimulateDatasetIdPost({
        datasetId,
        activityDurationReduction,
        capacityIncrease,
        numSimulations = 1000,
    }: {
        datasetId: string,
        /**
         * Activity duration reduction (0-1)
         */
        activityDurationReduction?: number,
        /**
         * Capacity increase (0-1)
         */
        capacityIncrease?: number,
        /**
         * Number of Monte Carlo iterations
         */
        numSimulations?: number,
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static detectJourneyDropoffsApiV1BusinessCustomerJourneyDropoffsDatasetIdGet({
        datasetId,
        expectedPath,
    }: {
        datasetId: string,
        /**
         * Expected journey path (comma-separated)
         */
        expectedPath?: (string | null),
    }): CancelablePromise<any> {
        return __request(OpenAPI, {
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
