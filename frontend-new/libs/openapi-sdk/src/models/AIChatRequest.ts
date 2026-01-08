/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChatMessage } from './ChatMessage';
/**
 * Request for AI chat completion.
 */
export type AIChatRequest = {
    /**
     * Dataset ID for process context
     */
    dataset_id: string;
    /**
     * User message
     */
    message: string;
    /**
     * Previous conversation for context
     */
    conversation_history?: Array<ChatMessage>;
    /**
     * Focus area: bottleneck, rework, pattern, cycle_time, summary
     */
    analysis_type?: (string | null);
};

