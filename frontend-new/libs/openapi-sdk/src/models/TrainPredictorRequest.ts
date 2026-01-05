/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request to train a prediction model.
 */
export type TrainPredictorRequest = {
    /**
     * Prediction target: 'next_activity', 'remaining_time', 'outcome'
     */
    target_type: string;
    /**
     * ML algorithm: 'random_forest', 'xgboost', 'gradient_boosting'
     */
    algorithm?: string;
    /**
     * Attribute to predict for outcome models
     */
    outcome_attribute?: (string | null);
};

