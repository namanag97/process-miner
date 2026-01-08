/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuditService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Audit Logs
     * Get audit logs (stub - returns empty list).
     * @param page
     * @param pageSize
     * @param actionType
     * @param entityType
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public getAuditLogsApiV1AuditLogsGet(
        page: number = 1,
        pageSize: number = 50,
        actionType?: (string | null),
        entityType?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/audit/logs',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'page': page,
                'page_size': pageSize,
                'action_type': actionType,
                'entity_type': entityType,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Audit Log
     * Create audit log entry (stub - accepts but discards).
     * @param xOrgId
     * @returns any Successful Response
     * @throws ApiError
     */
    public createAuditLogApiV1AuditLogsPost(
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/audit/logs',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
