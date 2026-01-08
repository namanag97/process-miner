/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { AIInsight } from './AIInsight';
/**
 * Response from AI chat endpoint.
 */
export type AIChatResponse = {
    /**
     * AI response content
     */
    message: string;
    insights?: Array<AIInsight>;
    context_used?: (string | null);
    /**
     * LLM model used
     */
    model?: string;
    tokens_used?: (number | null);
};

