/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DevDataService {
    /**
     * List Tables
     * List all tables in the database.
     * @returns string Successful Response
     * @throws ApiError
     */
    public static listTablesApiV1DevDataTablesGet(): CancelablePromise<Array<string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dev/data/tables',
        });
    }
    /**
     * Get Records
     * Get records from a table with pagination.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRecordsApiV1DevDataRecordsTableGet({
        table,
        limit = 20,
        offset,
    }: {
        table: string,
        limit?: number,
        offset?: number,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dev/data/records/{table}',
            path: {
                'table': table,
            },
            query: {
                'limit': limit,
                'offset': offset,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Record
     * Get a single record by ID.
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRecordApiV1DevDataRecordTableRecordIdGet({
        table,
        recordId,
    }: {
        table: string,
        recordId: string,
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/dev/data/record/{table}/{record_id}',
            path: {
                'table': table,
                'record_id': recordId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
