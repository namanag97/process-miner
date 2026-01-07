/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BottleneckResponse } from './BottleneckResponse';
import type { CycleTimeResponse } from './CycleTimeResponse';
import type { ThroughputResponse } from './ThroughputResponse';
/**
 * Performance summary dashboard.
 */
export type PerformanceDashboardResponse = {
    dataset_id: string;
    cycle_time: CycleTimeResponse;
    throughput: ThroughputResponse;
    top_bottlenecks: Array<BottleneckResponse>;
    rework_summary: Record<string, any>;
};

