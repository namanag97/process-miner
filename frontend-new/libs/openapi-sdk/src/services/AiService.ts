/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AICapabilitiesResponse } from '../models/AICapabilitiesResponse';
import type { AIChatRequest } from '../models/AIChatRequest';
import type { AIChatResponse } from '../models/AIChatResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AiService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Chat
     * Send a message to the AI assistant for process analysis.
     *
     * The AI assistant uses process analytics data (bottlenecks, cycle times,
     * rework patterns) to provide contextual, data-driven responses.
     *
     * Args:
     * request: Chat request with message and dataset_id
     * user: Current authenticated user
     * query_bus: CQRS query bus for fetching analytics
     *
     * Returns:
     * AIChatResponse with AI-generated message and optional insights
     * @param requestBody
     * @param xOrgId
     * @returns AIChatResponse Successful Response
     * @throws ApiError
     */
    public chatApiV1AiChatPost(
        requestBody: AIChatRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<AIChatResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/ai/chat',
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Capabilities
     * Get AI assistant capabilities and configuration.
     *
     * Returns information about what the AI can do and its current limits.
     * @param xOrgId
     * @returns AICapabilitiesResponse Successful Response
     * @throws ApiError
     */
    public getCapabilitiesApiV1AiCapabilitiesGet(
        xOrgId?: (string | null),
    ): CancelablePromise<AICapabilitiesResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/ai/capabilities',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
