/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { WorkflowTaskResponse } from './WorkflowTaskResponse';
/**
 * Workflow execution tracking response.
 */
export type src__platform__workflows__schemas__WorkflowResponse = {
    id: string;
    /**
     * Temporal's workflow ID
     */
    temporal_workflow_id?: (string | null);
    /**
     * Temporal's run ID
     */
    temporal_run_id?: (string | null);
    /**
     * ingestion, discovery, conformance, prediction, export
     */
    workflow_type: string;
    /**
     * dataset, model, analysis
     */
    entity_type?: (string | null);
    entity_id?: (string | null);
    /**
     * pending, running, completed, failed, cancelled, timed_out
     */
    status: string;
    progress_percent?: number;
    /**
     * Human-readable current step
     */
    current_step?: (string | null);
    error_code?: (string | null);
    error_message?: (string | null);
    retry_count?: number;
    created_at: string;
    started_at?: (string | null);
    completed_at?: (string | null);
    /**
     * Task-level progress
     */
    tasks?: Array<WorkflowTaskResponse>;
};

