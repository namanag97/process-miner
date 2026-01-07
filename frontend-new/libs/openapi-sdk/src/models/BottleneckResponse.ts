/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Bottleneck detection result.
 */
export type BottleneckResponse = {
    activity: string;
    avg_waiting_time_seconds: number;
    avg_service_time_seconds: number;
    frequency: number;
    is_bottleneck: boolean;
    severity: string;
    preceding_activities?: Array<string>;
    following_activities?: Array<string>;
    bottleneck_impact_score?: number;
};

