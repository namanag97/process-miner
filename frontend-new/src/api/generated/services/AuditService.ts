/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class AuditService {
    /**
     * Get Audit Logs
     * Get audit logs (stub - returns empty list).
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getAuditLogsApiV1AuditLogsGet({
        page = 1,
        pageSize = 50,
        actionType,
        entityType,
        xOrgId,
    }: {
        page?: number,
        pageSize?: number,
        actionType?: (string | null),
        entityType?: (string | null),
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
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
     * @returns any Successful Response
     * @throws ApiError
     */
    public static createAuditLogApiV1AuditLogsPost({
        xOrgId,
    }: {
        xOrgId?: (string | null),
    }): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
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
