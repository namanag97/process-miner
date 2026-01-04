"""ORM to Schema Converters.

Centralized conversion functions for transforming SQLAlchemy ORM objects
to Pydantic response schemas. These converters handle complex transformations
that go beyond simple field mapping.

Usage:
    # In routers, instead of manual json.loads() calls:
    from src.models.converters import dataset_to_response, project_to_response

    return dataset_to_response(orm_dataset)
"""

import json
from typing import TYPE_CHECKING

from src.models.schemas import (
    AnalysisResponse,
    DatasetDetailResponse,
    DatasetResponse,
    FilterConfig,
    FilteredLogResponse,
    FilterStatistics,
    OCELLogResponse,
    ProjectResponse,
    WorkflowResponse,
)

if TYPE_CHECKING:
    from src.models.orm import Analysis, Dataset, OCELLog, Project, Workflow


def dataset_to_response(dataset: "Dataset") -> DatasetResponse:
    """Convert ORM Dataset to API response with JSON field parsing.

    Handles: activities_json → activities
    """
    return DatasetResponse.model_validate(dataset)


def dataset_to_detail_response(dataset: "Dataset") -> DatasetDetailResponse:
    """Convert ORM Dataset to detailed API response.

    Handles: activities_json → activities, statistics_json → statistics
    """
    activities = []
    if dataset.activities_json:
        try:
            activities = json.loads(dataset.activities_json)
        except (json.JSONDecodeError, TypeError):
            pass

    statistics = None
    if dataset.statistics_json:
        try:
            statistics = json.loads(dataset.statistics_json)
        except (json.JSONDecodeError, TypeError):
            pass

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        activities=activities,
        created_at=dataset.created_at,
        source_file=dataset.source_file,
        status=dataset.status,
        statistics=statistics,
        updated_at=dataset.updated_at,
    )


def project_to_response(project: "Project") -> ProjectResponse:
    """Convert ORM Project to API response with JSON field parsing.

    Handles: tags_json → tags
    """
    return ProjectResponse.model_validate(project)


def analysis_to_response(analysis: "Analysis") -> AnalysisResponse:
    """Convert ORM Analysis to API response with JSON field parsing.

    Handles: config_json → config, result_summary_json → result_summary
    """
    return AnalysisResponse.model_validate(analysis)


def workflow_to_response(workflow: "Workflow") -> WorkflowResponse:
    """Convert ORM Workflow to API response with JSON field parsing.

    Handles: steps_json → steps
    """
    return WorkflowResponse.model_validate(workflow)


def ocel_log_to_response(log: "OCELLog") -> OCELLogResponse:
    """Convert ORM OCELLog to API response with metadata parsing.

    Handles: metadata_json → object_types, activities
    """
    metadata = {}
    if log.metadata_json:
        try:
            metadata = json.loads(log.metadata_json)
        except (json.JSONDecodeError, TypeError):
            pass

    return OCELLogResponse(
        id=log.id,
        name=log.name,
        source_file=log.source_file,
        source_format=log.source_format,
        total_events=log.total_events,
        total_objects=log.total_objects,
        total_object_types=log.total_object_types,
        object_types=metadata.get("object_types", []),
        activities=metadata.get("activities", []),
        created_at=log.created_at,
    )


def filtered_dataset_to_response(dataset: "Dataset") -> FilteredLogResponse:
    """Convert filtered ORM Dataset to FilteredLogResponse.

    Handles: filter_config_json → filter_config, filter_stats_json → statistics
    """
    filter_config = []
    if dataset.filter_config_json:
        try:
            config_list = json.loads(dataset.filter_config_json)
            filter_config = [FilterConfig(**c) for c in config_list]
        except (json.JSONDecodeError, TypeError):
            pass

    statistics = None
    if dataset.filter_stats_json:
        try:
            stats_dict = json.loads(dataset.filter_stats_json)
            statistics = FilterStatistics(**stats_dict)
        except (json.JSONDecodeError, TypeError):
            pass

    return FilteredLogResponse(
        id=dataset.id,
        name=dataset.name,
        source_dataset_id=dataset.source_dataset_id or "",
        is_filtered=dataset.is_filtered,
        filter_config=filter_config,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        statistics=statistics,
        created_at=dataset.created_at,
    )
