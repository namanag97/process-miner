/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Structured insight from AI analysis.
 */
export type AIInsight = {
    /**
     * bottleneck, pattern, anomaly, recommendation, metric
     */
    type: string;
    title: string;
    description: string;
    /**
     * high, medium, low, info
     */
    severity?: (string | null);
    data?: (Record<string, any> | null);
};

