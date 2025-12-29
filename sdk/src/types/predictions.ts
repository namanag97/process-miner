/**
 * Predictions Types - ML-based Process Predictions
 *
 * TODO: These types should be auto-generated from OpenAPI spec
 * For now, they match the backend Pydantic schemas
 */

export interface TrainPredictorRequest {
  target_type: "next_activity" | "outcome" | "remaining_time";
  algorithm?: string;
  model_name?: string;
  hyperparameters?: Record<string, any>;
}

export interface PredictorResponse {
  predictor_id: string;
  log_id: string;
  model_name: string;
  target_type: string;
  algorithm: string;
  status: "training" | "ready" | "failed";
  accuracy?: number;
  f1_score?: number;
  mae?: number;
  rmse?: number;
  training_time?: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
  result?: PredictorResponse;
  error?: string;
  created_at: string;
  updated_at?: string;
}

export interface PredictorListResponse {
  log_id: string;
  predictors: PredictorResponse[];
  total: number;
}

export interface PredictionRequest {
  case_prefix: Array<{
    activity: string;
    timestamp?: string;
    resource?: string;
  }>;
}

export interface PredictionResponse {
  predictor_id: string;
  prediction: {
    next_activity?: string;
    outcome?: string;
    remaining_time?: number;
    confidence?: number;
  };
  alternatives?: Array<{
    value: string | number;
    probability: number;
  }>;
}

export interface BatchPredictionRequest {
  cases: Array<{
    case_id: string;
    prefix: Array<{
      activity: string;
      timestamp?: string;
      resource?: string;
    }>;
  }>;
}

export interface BatchPredictionResponse {
  predictor_id: string;
  predictions: Array<{
    case_id: string;
    prediction: {
      next_activity?: string;
      outcome?: string;
      remaining_time?: number;
      confidence?: number;
    };
  }>;
  total_cases: number;
}
