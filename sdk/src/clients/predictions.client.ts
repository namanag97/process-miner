/**
 * Predictions Client - ML-based Process Prediction Operations
 *
 * Business verbs:
 * - trainPredictor() - Train a prediction model on event log
 * - getTrainingJob() - Get status of async training job
 * - listPredictors() - List all predictors for a log
 * - getPredictor() - Get predictor details
 * - predict() - Make a prediction for a case prefix
 * - predictBatch() - Make batch predictions for multiple cases
 * - deletePredictor() - Remove a predictor
 */

import { HttpClient } from "../client.js";
import {
  TrainPredictorRequest,
  PredictorResponse,
  JobStatusResponse,
  PredictorListResponse,
  PredictionRequest,
  PredictionResponse,
  BatchPredictionRequest,
  BatchPredictionResponse,
} from "../types/predictions.js";

export class PredictionsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Train a prediction model on an event log.
   * @param asyncMode - If true, returns job_id immediately; if false, waits for training to complete
   */
  async trainPredictor(
    logId: string,
    request: TrainPredictorRequest,
    asyncMode: boolean = false
  ): Promise<PredictorResponse | JobStatusResponse> {
    const response = await this.http.post<PredictorResponse | JobStatusResponse>(
      `/api/v1/predictions/logs/${logId}/train?async_mode=${asyncMode}`,
      request
    );
    return response;
  }

  /**
   * Get status of an async training job.
   */
  async getTrainingJob(jobId: string): Promise<JobStatusResponse> {
    return this.http.get<JobStatusResponse>(`/api/v1/predictions/jobs/${jobId}`);
  }

  /**
   * List all predictors for an event log.
   */
  async listPredictors(logId: string): Promise<PredictorListResponse> {
    return this.http.get<PredictorListResponse>(`/api/v1/predictions/logs/${logId}/predictors`);
  }

  /**
   * Get predictor details.
   */
  async getPredictor(predictorId: string): Promise<PredictorResponse> {
    return this.http.get<PredictorResponse>(`/api/v1/predictions/predictors/${predictorId}`);
  }

  /**
   * Make a prediction for a case prefix.
   * Predicts next activity, outcome, or remaining time.
   */
  async predict(predictorId: string, request: PredictionRequest): Promise<PredictionResponse> {
    return this.http.post<PredictionResponse>(
      `/api/v1/predictions/predictors/${predictorId}/predict`,
      request
    );
  }

  /**
   * Make batch predictions for multiple cases.
   * More efficient than individual predictions.
   */
  async predictBatch(
    predictorId: string,
    request: BatchPredictionRequest
  ): Promise<BatchPredictionResponse> {
    return this.http.post<BatchPredictionResponse>(
      `/api/v1/predictions/predictors/${predictorId}/predict-batch`,
      request
    );
  }

  /**
   * Delete a predictor and its associated model.
   */
  async deletePredictor(predictorId: string): Promise<void> {
    await this.http.delete(`/api/v1/predictions/predictors/${predictorId}`);
  }
}
