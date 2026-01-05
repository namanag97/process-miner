/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class DevDataService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Tables
     * List all tables in the database.
     * @returns string Successful Response
     * @throws ApiError
     */
    public listTablesApiV1DevDataTablesGet(): CancelablePromise<Array<string>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/dev/data/tables',
        });
    }
    /**
     * Get Records
     * Get records from a table with pagination.
     * @param table
     * @param limit
     * @param offset
     * @returns any Successful Response
     * @throws ApiError
     */
    public getRecordsApiV1DevDataRecordsTableGet(
        table: string,
        limit: number = 20,
        offset?: number,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
     * @param table
     * @param recordId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getRecordApiV1DevDataRecordTableRecordIdGet(
        table: string,
        recordId: string,
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
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
