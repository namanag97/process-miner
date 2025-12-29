/**
 * Workflows Client - Workflow Automation
 *
 * Business verbs:
 * - listPipelines() - Get available workflow pipelines
 * - start() - Start a workflow pipeline
 * - listExecutions() - Get workflow executions
 * - getExecution() - Get execution status
 * - cancel() - Cancel running execution
 */

import { HttpClient } from "../client.js";
import { WorkflowPipeline, WorkflowExecution, StartWorkflowOptions } from "../types/workflows.js";

export class WorkflowsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * List available workflow pipelines.
   */
  async listPipelines(): Promise<WorkflowPipeline[]> {
    return this.http.get<WorkflowPipeline[]>("/workflows/pipelines");
  }

  /**
   * Start a workflow pipeline.
   */
  async start(options: StartWorkflowOptions): Promise<WorkflowExecution> {
    return this.http.post<WorkflowExecution>("/workflows/start", {
      pipeline_name: options.pipelineName,
      log_id: options.logId,
      parameters: options.parameters,
    });
  }

  /**
   * List workflow executions.
   */
  async listExecutions(): Promise<WorkflowExecution[]> {
    return this.http.get<WorkflowExecution[]>("/workflows/executions");
  }

  /**
   * Get workflow execution status.
   */
  async getExecution(executionId: string): Promise<WorkflowExecution> {
    return this.http.get<WorkflowExecution>(`/workflows/executions/${executionId}`);
  }

  /**
   * Cancel a running workflow execution.
   */
  async cancel(executionId: string): Promise<void> {
    await this.http.post(`/workflows/executions/${executionId}/cancel`);
  }
}
