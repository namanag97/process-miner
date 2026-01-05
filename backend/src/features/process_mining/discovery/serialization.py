"""Model Serialization - Serialize/deserialize PM4Py models.

Supports joblib format (recommended) and legacy pickle format.
"""

import io
from typing import Any

import joblib

from src.features.process_mining.enums import ModelFormat
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class ModelSerializer:
    """Handles serialization and deserialization of PM4Py models."""

    def serialize(self, model_data: Any) -> bytes:
        """Serialize model for storage using joblib.

        Args:
            model_data: PM4Py model object (Petri net, DFG, Process tree, etc.)

        Returns:
            Serialized bytes (joblib format)
        """
        buffer = io.BytesIO()
        joblib.dump(model_data, buffer)
        return buffer.getvalue()

    def deserialize(self, data: bytes) -> Any:
        """Deserialize model from storage.

        Supports both new joblib format and legacy pickle format.

        Args:
            data: Serialized model bytes

        Returns:
            PM4Py model object
        """
        try:
            buffer = io.BytesIO(data)
            return joblib.load(buffer)
        except Exception:
            from src.platform.core.safe_unpickler import safe_loads

            logger.warning(
                "deserializing_legacy_pickle_model",
                msg="Consider re-discovering model to use joblib format",
            )
            return safe_loads(data)

    def to_graph_json(self, model_data: Any, model_format: ModelFormat) -> dict[str, Any] | None:
        """Serialize model to frontend-ready graph JSON.

        Args:
            model_data: The model data from discovery
            model_format: The format of the model

        Returns:
            Graph JSON dict or None if not supported
        """
        from src.features.process_mining.services.serializers import GraphStructureSerializer

        serializer = GraphStructureSerializer()

        try:
            if model_format == ModelFormat.DFG:
                dfg, start_activities, end_activities = model_data
                return serializer.serialize_dfg(dfg, start_activities, end_activities)

            if model_format == ModelFormat.PERFORMANCE_DFG:
                dfg, start_activities, end_activities = model_data
                return serializer.serialize_dfg(dfg, start_activities, end_activities)

            if model_format == ModelFormat.PETRI_NET:
                net, im, fm = model_data
                return serializer.serialize_petri_net(net, im, fm)

            if model_format == ModelFormat.PROCESS_TREE:
                import pm4py

                net, im, fm = pm4py.convert_to_petri_net(model_data)
                graph_json = serializer.serialize_petri_net(net, im, fm)
                graph_json["metadata"]["source_format"] = "process_tree"
                return graph_json

            if model_format == ModelFormat.DECLARE:
                return self._serialize_declare(model_data)

            if model_format == ModelFormat.LOG_SKELETON:
                return self._serialize_log_skeleton(model_data)

            if model_format == ModelFormat.TEMPORAL_PROFILE:
                return self._serialize_temporal_profile(model_data)

            if model_format == ModelFormat.BATCHES:
                return self._serialize_batches(model_data)

            logger.debug(
                "graph_json_serialization_not_supported",
                model_format=model_format.value,
            )
            return None

        except Exception as e:
            logger.warning(
                "graph_json_serialization_failed",
                model_format=model_format.value,
                error=str(e),
            )
            return None

    def _serialize_declare(self, model_data: Any) -> dict[str, Any]:
        """Serialize DECLARE model."""
        if isinstance(model_data, dict):
            return {
                "type": "declare",
                "constraints": model_data.get("constraints", []),
                "activities": model_data.get("activities", []),
                "metadata": {"type": "declare", "error": model_data.get("error")},
            }
        return {
            "type": "declare",
            "constraints": [],
            "activities": list(getattr(model_data, "activities", set())),
            "metadata": {"type": "declare", "source": "pm4py"},
        }

    def _serialize_log_skeleton(self, model_data: Any) -> dict[str, Any]:
        """Serialize Log Skeleton model."""

        def convert_sets(obj):
            if isinstance(obj, set):
                return list(obj)
            if isinstance(obj, dict):
                return {k: convert_sets(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple)):
                return [convert_sets(item) for item in obj]
            return obj

        if isinstance(model_data, dict):
            return {
                "type": "log_skeleton",
                "constraints": convert_sets(model_data),
                "metadata": {"type": "log_skeleton"},
            }
        return {
            "type": "log_skeleton",
            "data": str(model_data),
            "metadata": {"type": "log_skeleton"},
        }

    def _serialize_temporal_profile(self, model_data: Any) -> dict[str, Any]:
        """Serialize Temporal Profile model."""
        if isinstance(model_data, dict):
            return {
                "type": "temporal_profile",
                "profiles": model_data,
                "metadata": {"type": "temporal_profile"},
            }
        return {
            "type": "temporal_profile",
            "data": str(model_data),
            "metadata": {"type": "temporal_profile"},
        }

    def _serialize_batches(self, model_data: Any) -> dict[str, Any]:
        """Serialize Batches model."""
        if isinstance(model_data, (list, tuple)):
            return {
                "type": "batches",
                "batches": list(model_data),
                "metadata": {"type": "batches", "count": len(model_data)},
            }
        return {
            "type": "batches",
            "data": str(model_data),
            "metadata": {"type": "batches"},
        }


# Singleton instance
model_serializer = ModelSerializer()
