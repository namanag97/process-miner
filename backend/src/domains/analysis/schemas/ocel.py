"""OCEL schemas - Object-Centric Event Log support.

Contains schemas for:
- OCEL log upload and responses
- Object-Centric DFG (OC-DFG)
- Object-Centric Petri Nets
- Object interaction graphs
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, model_validator


class OCELUploadRequest(BaseModel):
    """Request for OCEL file upload."""

    name: str | None = None


class OCELLogResponse(BaseModel):
    """OCEL log response."""

    id: str
    name: str
    source_file: str | None
    source_format: str
    total_events: int
    total_objects: int
    total_object_types: int
    object_types: list[str] = []
    activities: list[str] = []
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse metadata_json to object_types and activities."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "name",
                    "source_file",
                    "source_format",
                    "total_events",
                    "total_objects",
                    "total_object_types",
                    "metadata_json",
                    "created_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("metadata_json"):
                try:
                    metadata = json.loads(data["metadata_json"])
                    # object_types is extracted from objects_per_type keys (ORM storage format)
                    data["object_types"] = list(metadata.get("objects_per_type", {}).keys())
                    data["activities"] = metadata.get("activities", [])
                except (json.JSONDecodeError, TypeError):
                    data["object_types"] = []
                    data["activities"] = []
            else:
                if "object_types" not in data:
                    data["object_types"] = []
                if "activities" not in data:
                    data["activities"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


class OCELLogListResponse(BaseModel):
    """List of OCEL logs."""

    logs: list[OCELLogResponse]
    total: int


class OCELObjectTypeResponse(BaseModel):
    """Object type in an OCEL."""

    name: str
    object_count: int
    attributes: list[str] = []


class OCELStatisticsResponse(BaseModel):
    """OCEL statistics response."""

    dataset_id: str
    total_events: int
    total_objects: int
    total_object_types: int
    total_activities: int
    object_types: list[str]
    activities: list[str]
    objects_per_type: dict[str, int]


class DiscoverOCPNRequest(BaseModel):
    """Request to discover Object-Centric Petri Net."""

    dataset_id: str
    model_name: str | None = None


class OCPetriNetResponse(BaseModel):
    """Object-Centric Petri Net response."""

    id: str
    dataset_id: str = ""
    name: str
    object_types: list[str] = []
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse object_types_json to object_types list."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in ["id", "dataset_id", "name", "object_types_json", "created_at"]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("object_types_json"):
                try:
                    data["object_types"] = json.loads(data["object_types_json"])
                except (json.JSONDecodeError, TypeError):
                    data["object_types"] = []
            elif "object_types" not in data:
                data["object_types"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Object-Centric DFG
# =============================================================================


class OCDFGNode(BaseModel):
    """Object-Centric DFG node."""

    id: str
    name: str
    object_type: str
    frequency: int = 0


class OCDFGEdge(BaseModel):
    """Object-Centric DFG edge."""

    source: str
    target: str
    object_type: str
    frequency: int


class OCDFGTypeGraph(BaseModel):
    """OC-DFG graph for a single object type."""

    object_type: str
    nodes: list[OCDFGNode]
    edges: list[OCDFGEdge]
    start_activities: list[str] = []
    end_activities: list[str] = []


class OCDFGResponse(BaseModel):
    """Object-Centric DFG response."""

    dataset_id: str
    object_types: list[str]
    activities: list[str]
    graphs_by_type: dict[str, OCDFGTypeGraph]
    total_events: int = 0
    total_objects: int = 0


class FlattenedLogInfo(BaseModel):
    """Info about a flattened OCEL."""

    object_type: str
    case_count: int
    event_count: int


# =============================================================================
# Object Interaction Graph
# =============================================================================


class ObjectGraphNode(BaseModel):
    """Node in object interaction graph."""

    id: str
    object_type: str


class ObjectGraphEdge(BaseModel):
    """Edge in object interaction graph."""

    source: str
    target: str
    relationship: str = ""


class ObjectGraphResponse(BaseModel):
    """Object interaction graph response."""

    nodes: list[ObjectGraphNode]
    edges: list[ObjectGraphEdge]
