/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Single bottleneck result.
 */
export type BottleneckResponse = {
    activity: string;
    /**
     * Average wait time in seconds
     */
    avg_waiting_time_seconds: number;
    /**
     * Average service time in seconds
     */
    avg_service_time_seconds?: number;
    /**
     * Number of occurrences
     */
    frequency: number;
    /**
     * Whether this is flagged as a bottleneck
     */
    is_bottleneck?: boolean;
    /**
     * Severity level: low, medium, high
     */
    severity?: string;
    /**
     * Activities that precede this one
     */
    preceding_activities?: Array<string>;
    /**
     * Activities that follow this one
     */
    following_activities?: Array<string>;
    /**
     * Impact score 0-1
     */
    bottleneck_impact_score?: number;
};

