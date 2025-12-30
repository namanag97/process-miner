"""Prediction Service - ML-based Process Predictions.

Provides next activity prediction, remaining time prediction,
and outcome prediction using scikit-learn and XGBoost.
"""

import pickle
import time

import numpy as np
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class PredictionService:
    """ML prediction service for process mining."""

    def extract_features(self, pm4py_log: PM4PyLog) -> tuple[list, list, list]:
        """Extract features from event log for ML training."""
        logger.info("extracting_features", traces=len(pm4py_log))
        start = time.perf_counter()

        all_activities = set()
        for trace in pm4py_log:
            for event in trace:
                all_activities.add(event.get("concept:name", ""))
        activity_list = sorted(list(all_activities))
        activity_to_idx = {a: i for i, a in enumerate(activity_list)}

        X, y_next, y_time = [], [], []

        for trace in pm4py_log:
            activities = [e.get("concept:name", "") for e in trace]
            timestamps = [e.get("time:timestamp") for e in trace if "time:timestamp" in e]

            for i in range(1, len(activities)):
                prefix = activities[:i]
                prefix_encoded = [0] * len(activity_list)
                for a in prefix[-5:]:
                    if a in activity_to_idx:
                        prefix_encoded[activity_to_idx[a]] = 1

                features = prefix_encoded + [len(prefix), i / len(activities)]
                X.append(features)
                y_next.append(activity_to_idx.get(activities[i], 0))

                if len(timestamps) > i:
                    remaining = (timestamps[-1] - timestamps[i - 1]).total_seconds()
                    y_time.append(remaining)
                else:
                    y_time.append(0)

        duration = (time.perf_counter() - start) * 1000
        logger.info("features_extracted", samples=len(X), duration_ms=round(duration, 2))
        return X, y_next, y_time

    def train_next_activity_model(self, pm4py_log: PM4PyLog, algorithm: str = "random_forest") -> tuple[bytes, dict]:
        """Train next activity prediction model."""
        logger.info("training_next_activity_model", algorithm=algorithm, traces=len(pm4py_log))
        start = time.perf_counter()

        X, y_next, _ = self.extract_features(pm4py_log)
        if not X:
            return b"", {"error": "No training data"}

        X, y = np.array(X), np.array(y_next)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        if algorithm == "xgboost":
            try:
                from xgboost import XGBClassifier
                model = XGBClassifier(n_estimators=100, max_depth=5, use_label_encoder=False, eval_metric='mlogloss')
            except ImportError:
                from sklearn.ensemble import RandomForestClassifier
                model = RandomForestClassifier(n_estimators=100, max_depth=10)
        else:
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(n_estimators=100, max_depth=10)

        model.fit(X_train, y_train)
        accuracy = model.score(X_test, y_test) if len(X_test) > 0 else 0

        model_bytes = pickle.dumps(model)
        metrics = {"accuracy": round(float(accuracy), 4), "train_samples": len(X_train), "test_samples": len(X_test)}

        duration = (time.perf_counter() - start) * 1000
        logger.info("model_trained", accuracy=metrics["accuracy"], duration_ms=round(duration, 2))
        return model_bytes, metrics

    def train_remaining_time_model(self, pm4py_log: PM4PyLog, algorithm: str = "random_forest") -> tuple[bytes, dict]:
        """Train remaining time prediction model."""
        logger.info("training_remaining_time_model", algorithm=algorithm, traces=len(pm4py_log))
        start = time.perf_counter()

        X, _, y_time = self.extract_features(pm4py_log)
        if not X:
            return b"", {"error": "No training data"}

        X, y = np.array(X), np.array(y_time)
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        if algorithm == "xgboost":
            try:
                from xgboost import XGBRegressor
                model = XGBRegressor(n_estimators=100, max_depth=5)
            except ImportError:
                from sklearn.ensemble import RandomForestRegressor
                model = RandomForestRegressor(n_estimators=100, max_depth=10)
        else:
            from sklearn.ensemble import RandomForestRegressor
            model = RandomForestRegressor(n_estimators=100, max_depth=10)

        model.fit(X_train, y_train)

        if len(X_test) > 0:
            predictions = model.predict(X_test)
            mae = np.mean(np.abs(predictions - y_test))
            rmse = np.sqrt(np.mean((predictions - y_test) ** 2))
        else:
            mae, rmse = 0, 0

        model_bytes = pickle.dumps(model)
        metrics = {"mae_seconds": round(float(mae), 2), "rmse_seconds": round(float(rmse), 2),
                   "train_samples": len(X_train), "test_samples": len(X_test)}

        duration = (time.perf_counter() - start) * 1000
        logger.info("model_trained", mae=metrics["mae_seconds"], duration_ms=round(duration, 2))
        return model_bytes, metrics

    def predict_next_activity(self, model_bytes: bytes, case_prefix: list[str], activities: list[str]) -> dict:
        """Predict next activity for a case prefix."""
        if not model_bytes:
            return {"prediction": None, "confidence": 0}

        model = pickle.loads(model_bytes)
        activity_to_idx = {a: i for i, a in enumerate(activities)}

        prefix_encoded = [0] * len(activities)
        for a in case_prefix[-5:]:
            if a in activity_to_idx:
                prefix_encoded[activity_to_idx[a]] = 1

        features = np.array([prefix_encoded + [len(case_prefix), 0.5]])

        prediction_idx = model.predict(features)[0]
        probas = model.predict_proba(features)[0] if hasattr(model, 'predict_proba') else [1.0]

        predicted_activity = activities[int(prediction_idx)] if int(prediction_idx) < len(activities) else activities[0]
        confidence = float(max(probas))

        alternatives = []
        if hasattr(model, 'predict_proba'):
            sorted_idx = np.argsort(probas)[::-1][:3]
            for idx in sorted_idx:
                if idx < len(activities):
                    alternatives.append({"activity": activities[idx], "probability": round(float(probas[idx]), 4)})

        return {"prediction": predicted_activity, "confidence": round(confidence, 4), "alternatives": alternatives}

    def predict_remaining_time(self, model_bytes: bytes, case_prefix: list[str], activities: list[str]) -> dict:
        """Predict remaining time for a case prefix."""
        if not model_bytes:
            return {"prediction_seconds": 0, "confidence": 0}

        model = pickle.loads(model_bytes)
        activity_to_idx = {a: i for i, a in enumerate(activities)}

        prefix_encoded = [0] * len(activities)
        for a in case_prefix[-5:]:
            if a in activity_to_idx:
                prefix_encoded[activity_to_idx[a]] = 1

        features = np.array([prefix_encoded + [len(case_prefix), 0.5]])
        prediction = model.predict(features)[0]

        return {"prediction_seconds": round(float(prediction), 2), "confidence": 0.8}

    def get_activities_from_log(self, pm4py_log: PM4PyLog) -> list[str]:
        """Get sorted list of activities from log."""
        activities = set()
        for trace in pm4py_log:
            for event in trace:
                activities.add(event.get("concept:name", ""))
        return sorted(list(activities))


prediction_service = PredictionService()
